import os
import numpy as np
import csv
import cv2
from PIL import Image, ImageFont, ImageDraw
import imgkit


# rgb 인풋 이미지와 mask 결과 이미지의 파일네임은 같아야 하며, rgb input = .jpg mask result = .png 확장자를 갖고 있어야 합니다.
RGB_SRC = '/home/islab/Desktop/images' # RGB 인풋 이미지 폴더
MASK_SRC = '/home/islab/Desktop/polygon' # 마스크 결과 폴더
MAP_SRC = '/home/islab/Desktop/tp_monitoring/map.png' # 카카오 지도 이미지
GPS_SRC = '/home/islab/Desktop/tp_monitoring/gps_record.csv' # GPS 데이터 CSV 파일
FOOTSTEP_ICON_PATH = '/home/islab/Desktop/footsteps-silhouette-variant.png' # 발자국 아이콘   
OUT_PATH = 'result.avi'


GREEN = [0,255,0] # 보행가능영역 마스크 값
RATE = 80 # 발자국 픽셀 간격
MAP_CORDINATE = [1500, 770] # 지도 표시 위치
FPS = 60 # 생성될 동영상 프레임

options = {
    'format': 'png',    
    'crop-w': '420',
} # 맵 캡쳐 옵션

# 실시간 지도 업데이트가 필요할시 아래의 func 를 실행하면 latlan 에 따라 map.png 가 업데이트 됩니다.
def update_map(lat, lan):             
   imgkit.from_url(f'http://localhost:3000/?lat={lat}&lan={lan}', 'map.png', options=options)    
        
# csv 파일로 부터 gps 리스트 생성
def get_gps_record(gps_csv):
    gps_list = []
    with open(gps_csv, newline='') as csvfile:    
        reader = csv.DictReader(csvfile)
        gps_list = []
        for row in reader:
            lat = row['lat']
            lan = row['lan']
            speed = row['speed(m/s)']
            gps_list.append([lat, lan, speed])
    return gps_list

# 발자국 위치 생성
def update_footstep_cordinate(mask):
    footstep_cordiate = []
    img_np = np.array(mask)    
    Y,X = np.where(np.all(img_np==GREEN,axis=2))
    y_max = Y.max()
    y_min = Y.min()
    for i in range(1, 1 + (y_max - y_min) // RATE):    
        y = y_max - i * RATE
        cal = img_np[y]
        g = np.where(np.all(cal==GREEN,axis=1))
        x = np.array(g).mean()        
        footstep_cordiate.append([int(x), y])
    return footstep_cordiate

# 생성된 지도, 발자국 마스크, 취합
def mix_image(rgb_path, mask, footstep_cordinates, latlan, footstep_icon, map_img, out):
    rgb = Image.open(rgb_path)    
    rgb_mask = Image.blend(rgb,mask,0.1) #rgb 에 mask를 10% overlay   
    for cordinate in footstep_cordinates:
        rgb_mask.paste(footstep_icon, cordinate, footstep_icon)
    rgb_mask.paste(map_img, MAP_CORDINATE)        
    fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 40) # 폰트
    d = ImageDraw.Draw(rgb_mask)
    d.multiline_text((10, 10), f"lat:{latlan[0]}\nlan:{latlan[1]}\nspeed:{latlan[2]}m/s", font=fnt, fill=(255, 255, 255))
    out.write(cv2.cvtColor(np.array(rgb_mask), cv2.COLOR_RGB2BGR))
    
def main():    
    rgb_list = sorted(os.listdir(RGB_SRC))
    mask_list = sorted(os.listdir(MASK_SRC))
    rgb_core_list = [rgb.replace('.jpg', '') for rgb in rgb_list]
    mask_core_list = [mask.replace('.png', '') for mask in mask_list]    
    
    gps_index = 0
    footstep_cordinates = []
    footstep_icon = Image.open(FOOTSTEP_ICON_PATH, 'r')  
    gps_list = get_gps_record(GPS_SRC)
    out = cv2.VideoWriter(OUT_PATH, cv2.VideoWriter_fourcc(*'DIVX'), FPS, (1920, 1080))
    mask_path = os.path.join(MASK_SRC, f'{mask_core_list[0]}.png')
    mask = Image.open(mask_path)
    map_img = Image.open(MAP_SRC, 'r')   
    for rgb in rgb_core_list:
        print(f'processing image {rgb}')
        try:                        
            if rgb in mask_core_list:
                mask_path = os.path.join(MASK_SRC, f'{rgb}.png')
                mask = Image.open(mask_path)
                footstep_cordinates = update_footstep_cordinate(mask)                
                gps_index = gps_index + 1
                # 실 GPS 데이터 이용시 삽입
                # update_map(lat, lan) 
                # map_img = Image.open(MAP_SRC, 'r')   
            rgb_path = os.path.join(RGB_SRC, f'{rgb}.jpg')
            mix_image(rgb_path, mask, footstep_cordinates, gps_list[gps_index], footstep_icon, map_img, out)
        except:
            pass
    out.release()    

if __name__ == "__main__":
    main()
    print('Done')
    