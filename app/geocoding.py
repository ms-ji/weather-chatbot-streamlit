import requests

def get_coordinates(city_name,state_code="",country_code="",api_key="",limit=5):
    """
    도시명으로부터 위도·경도를 얻는 함수

    Args:
        city_name (str): 도시명
        state_code (str): 주/도 코드 (선택사항)
        country_code (str): 국가 코드 (예: 'KR', 'US')
        api_key (str): OpenWeatherMap API 키
        limit (int): 반환할 결과 개수 (기본값: 5)

    Returns:
        list: 위치 정보 리스트 또는 빈 리스트
    """
    #검색 쿼리 구성
    query_parts = [city_name]
    if state_code:
        query_parts.append(state_code)
    if country_code:
        query_parts.append(country_code)

    query = ",".join(query_parts)

    url = f"https://api.openweathermap.org/geo/1.0/direct?q={query}&limit={limit}&appid={api_key}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if data: # 데이터가 있는지 확인
            locations = []
            for i, location in enumerate(data):
                location_info = {
                    'index': i,
                    'name': location['name'],
                    'lat': location['lat'],
                    'lon': location['lon'],
                    'country': location['country'],
                    'state': location.get('state', ''),  # state가 없을 수도 있음
                }
                locations.append(location_info)
                print(f"{i}: {location['name']}, {location.get('state', '')}, {location['country']} ({location['lat']}, {location['lon']})")
            return locations #location이 아닌 locations 반환
        else:
            print(f"'{query}'에 대한 결과를 찾을 수 없습니다.")
            return [] # 빈값 반환
    else:
        print(f"API 호출 실패: {response.status_code}")
        return []  # 빈값 반환

def get_single_coordinate(city_name,index=0,**kwargs):
    locations = get_coordinates(city_name, **kwargs)

    # 디버깅
    # print(type(locations), locations)

    if locations and 0 <= index < len(locations): # locations이 존재하고 인덱스가 유효한 범위 안에 있는가?
        location = locations[index]
        return location['lat'], location['lon']
    return None, None