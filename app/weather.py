import requests

def get_current_weather(lat,lon,api_key):
    """
    위도 경도로 현재 날씨 정보를 가져오는 함수
    """
    if not api_key:
        print(f"api키가 유효하지 않습니다.")
        return None

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # print(data)
        weather_info = {
            'location': data['name'],
            'description': data['weather'][0]['description'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data.get('wind', {}).get('speed', 0),
            'country': data['sys']['country']
        }
        return weather_info
    else:
        print(f"날씨 데이터 조회 실패 : {response.status_code}")
        return None