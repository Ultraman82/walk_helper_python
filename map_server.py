from flask import Flask, render_template_string, request

# API_KEY = '1f4b7f840486d6eaef49e9d86313f569'
API_KEY = '카카오맵 JS API 키'

def getKakaoMapHtml(lat, lan):    
    result = ""
    result = result + "<!DOCTYPE html>" + "\n"
    result = result + "<html>" + "\n"
    result = result + "    <head>" + "\n"
    result = result + "        <meta charset='utf-8'/>" + "\n"
    result = result + "            <title>Kakao 지도 시작하기</title>" + "\n"
    result = result + "    </head>" + "\n"
    result = result + "    <body>" + "\n"    
    result = result + "        <div id='map' style='width:400px;height:300px;display:inline-block;'></div>""\n"           
    result = result + f"        <script type='text/javascript' src='//dapi.kakao.com/v2/maps/sdk.js?appkey={API_KEY}'></script>" + "\n"
    result = result + "        <script>" + "\n"
    result = result + "            var container = document.getElementById('map'); " + "\n"
    result = result + "            var options = {" + "\n"    
    result = result + f"                   center: new kakao.maps.LatLng({lat}, {lan})," + "\n"
    result = result + "                   level: 3" + "\n"
    result = result + "            }; " + "\n"
    result = result + "            var map = new kakao.maps.StaticMap(container, options); " + "\n"
    result = result + "        </script>" + "\n"
    result = result + "    </body>" + "\n"
    result = result + "</html>" + "\n"    
    return result   
   
app = Flask('map_server')
latlan_index = 0
@app.route('/')
def index():      
   lat = request.args.get('lat')
   lan = request.args.get('lan')      
   map_html = getKakaoMapHtml(lat, lan)        
   return render_template_string(map_html)
app.run(host="localhost", port="3000")