import requests
import json
from urllib import parse
from collections import defaultdict

API_KEY = ''
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": API_KEY
}
def get_tier(s_id):
    url = f'https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}'
    
    while True:
        try:
            response = requests.get(url, headers=REQUEST_HEADERS)
            response_data = response.json()

            if not response_data:
                return "UNRANK"
            else:
                return response_data[0]['tier'] + " " + response_data[0]['rank']
        except requests.exceptions.RequestException as e:
            log_info(f"Error fetching match IDs: {e}. Break")
            return False

# 소환사별 특정 챔피언 숙련레벨 얻기 함수
def get_mastery(puuid, c_id):
    url = f"https://kr.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{c_id}"

    while True:
        try:
            response = requests.get(url, headers=REQUEST_HEADERS)
            response.raise_for_status()
            response_data = response.json()
            
            return response_data['championLevel']
        except requests.exceptions.RequestException as e:
            log_info(f"Error fetching data: {e}")
            return False
        
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
        
            #if match_data['gameMode'] == 'ARAM':
            return match_data
                
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return False

def fetch_match_data(match_data):
    for i in range(10):
        summonerID = match_data['participants'][i]['summonerId']
        tier = get_tier(summonerID)
        match_data['participants'][i]['tier'] = tier
        tier = match_data['participants'][i]['tier']
        
        puuid = match_data['participants'][i]['puuid']
        ci = match_data['participants'][i]['championId']
        
        champion_mastery = get_mastery(puuid, ci)
        match_data['participants'][i]['championMasteryLevel'] = champion_mastery
        champion_mastery = match_data['participants'][i]['championMasteryLevel']
        
    return match_data

def change_data(data, result):
    participants = data['participants']
    blue_team = [p for p in participants if p['teamId'] == 100]
    red_team = [p for p in participants if p['teamId'] == 200]

    for i, p in enumerate(blue_team):
        result[f"blue c{i+1}"] = p["championId"]
        result[f"blue-c{i+1}-tier"] = p["tier"]
        result[f"blue_c{i+1}-mastery"] = p["championMasteryLevel"]

    for i, p in enumerate(red_team):
        result[f"red c{i+1}"] = p["championId"]
        result[f"red-c{i+1}-tier"] = p["tier"]
        result[f"red_c{i+1}-mastery"] = p["championMasteryLevel"]

    result["duration"] = 20

#main
if __name__ == "__main__":
    nickname = input('Input Nickname: ')
    tag_line = input('Tag Line: ')
    
    puuid = get_puuid(nickname, tag_line)
    if not puuid:
        print('존재하지 않는 닉네임입니다.')
        
    else:
        data = get_match_data(puuid)
        data = fetch_match_data(data)
        
        result = defaultdict()
        change_data(data, result)
