import requests
import json
from urllib import parse

API_KEY = ''
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": API_KEY
}

def get_puuid(user_nickname, tag_line):
    encoded_name = parse.quote(user_nickname)
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_name}/{tag_line}"
    
    while True:
        try:
            response = requests.get(url, headers=REQUEST_HEADERS)
            response.raise_for_status()

            return response.json()['puuid']
       
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return False

def get_match_data(puuid):
    url = f"https://kr.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"
    
    while True:
        try:
            response = requests.get(url, headers=REQUEST_HEADERS)
            response.raise_for_status()
            match_data = response.json()
        
            if match_data['gameMode'] == 'ARAM':
                return match_data
                
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return False


#main
if __name__ == "__main__":
    nickname = input('Input Nickname: ')
    tag_line = input('Tag Line: ')
    
    puuid = get_puuid(nickname, tag_line)
    
    data = get_match_data(puuid)
    if not data:
        print("진행중인 게임이 칼바람나락이 아닙니다.")
    else:
        print(data)