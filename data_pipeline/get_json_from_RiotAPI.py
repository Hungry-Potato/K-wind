import requests
import json
from urllib import parse
import time
from datetime import datetime
from collections import defaultdict
import os

# Riot API 설정
API_KEY = ''
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": API_KEY
}

#소환사별 티어 얻기 함수
def get_tier(s_id):
    url = f'https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{s_id}'
    
    while True:
        try:
            response = requests.get(url, headers=REQUEST_HEADERS)
            
            if response.status_code == 429:
                rate_limit_sleep(10)
                continue  # 다시 시도
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
            
            if response.status_code == 429:
                rate_limit_sleep(10)
                continue
            
            response.raise_for_status()
            response_data = response.json()
            
            return response_data['championLevel']
        except requests.exceptions.RequestException as e:
            log_info(f"Error fetching data: {e}")
            return False

#로그 띄우기 및 로그 저장 함수
def log_info(message, log_file = '/laewon/Riot/logs/app.log', max_size = 1_000_000):
    if os.path.exists(log_file) and os.path.getsize(log_file) > max_size:
        backup_name = f"{log_file}.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        os.rename(log_file, backup_name)
        print(f"Log rotated: {backup_name}")

    with open(log_file, "a", encoding="utf-8") as file:
        log_entry = f"{datetime.now()} [INFO] {message}\n"
        file.write(log_entry)
    print(f"{datetime.now()} [INFO] {message}")

#시간 대기 함수
def rate_limit_sleep(time_period=1):
    log_info(f"Rate limit exceeded. Retrying after {time_period} second(s)...")
    time.sleep(time_period)

# 특정 소환사의 puuid 얻기 함수
def get_puuid(user_nickname, tag_line):
    encoded_name = parse.quote(user_nickname)
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_name}/{tag_line}"
    
    while True:
        try:
            response = requests.get(url, headers=REQUEST_HEADERS)
            if response.status_code == 429:
                rate_limit_sleep(10)
                continue
            response.raise_for_status()

            return response.json()['puuid']
       
        except requests.exceptions.RequestException as e:
            log_info(f"Error fetching data: {e}")
            return False

# 특정 소환사의 칼바람 matchId 얻기 함수
def get_match_ids(puuid, start=0, count=20, queue=450):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue={queue}&start={start}&count={count}"

    while True:
        try:
            response = requests.get(url, headers=REQUEST_HEADERS)
            
            if response.status_code == 429:
                rate_limit_sleep(10)
                continue
            
            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as e:
            log_info(f"Error fetching data: {e}")
            return False

# 특정 match id의 match 정보 얻기 함수
def get_match_data(match_id, idx):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}"
    log_info(f"Fetching match data for {idx + 1}th match: {match_id}")
    
    while True:
        try:
            response = requests.get(url, headers=REQUEST_HEADERS)
            
            if response.status_code == 429:
                rate_limit_sleep(10)
                continue
            
            response.raise_for_status()
            match_data = response.json()
        
            if match_data['info']['gameMode'] == 'ARAM':
                log_info(f"Match data retrieved for {match_id}")
                return match_data
            return None
        except requests.exceptions.RequestException as e:
            log_info(f"Error fetching data: {e}")
            return False

# 주요 실행 로직
def fetch_match_ids(puuid, limit=100):
    match_ids = []
    total_requests, start, count = 0, 0, 100
    
    while start != count:
        rate_limit_sleep(1.205)
        match_ids_batch = get_match_ids(puuid, start=start, count=count)
        if not match_ids_batch:
            break
        match_ids.extend(match_ids_batch)
        start = count
    
    log_info(f"Successfully fetched {len(match_ids)} match IDs.")
    return match_ids

# 주요 실행 로직
def fetch_match_data(match_ids, check_match_id):
    aram_matches = []
    
    for idx, match_id in enumerate(match_ids):
        if check_match_id[match_id]:
            continue
        
        check_match_id[match_id] = True
        rate_limit_sleep(1.205)  # 초당 요청 제한
        match_data = get_match_data(match_id, idx)
        
        if match_data:
            for i in range(10):
                print(i)
                summonerID = match_data['info']['participants'][i]['summonerId']
                rate_limit_sleep(1.205)
                log_info('get tier')
                tier = get_tier(summonerID)
                match_data['info']['participants'][i]['tier'] = tier
                tier = match_data['info']['participants'][i]['tier']
    
                puuid = match_data['info']['participants'][i]['puuid']
                ce = match_data['info']['participants'][i]['championId']
                rate_limit_sleep(1.205)
                log_info('get champ mastery')
                champion_mastery = get_mastery(puuid, ce)
                match_data['info']['participants'][i]['championMasteryLevel'] = champion_mastery
                champion_mastery = match_data['info']['participants'][i]['championMasteryLevel']
            print('------------------------------')
            aram_matches.append(match_data)
        
        log_file = '/laewon/Riot/logs/distinct_match_id.log'
        distinct_something(0, 0, match_id, log_file)
    
    log_info(f"Successfully fetched {len(aram_matches)} ARAM match data.")
    return aram_matches

#데이터 저장 함수
def save_to_file(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    log_info(f"Data saved to {file_path}")


# 다음 유저 정보 얻기
def next_user_name(USER_NICKNAME, TAG_LINE, aram_match, check_nickname):
    for i in range(10):
        next_user = aram_matches[0]['info']['participants'][i]['riotIdGameName']
        next_user_tag_line = aram_matches[0]['info']['participants'][i]['riotIdTagline']
        if not check_nickname[next_user + next_user_tag_line]:
            USER_NICKNAME = next_user
            TAG_LINE = next_user_tag_line
            break
    log_file = '/laewon/Riot/logs/distinct_nickname.log'
    distinct_something(USER_NICKNAME, TAG_LINE, 0, log_file)

    return USER_NICKNAME, TAG_LINE

# 이미 확인한 매치 아이디, 유저 저장
def distinct_something(USER_NICKNAME, TAG_LINE, match_id, log_file, max_size = 1_000_000):
    if os.path.exists(log_file) and os.path.getsize(log_file) > max_size:
        backup_name = f"{log_file}.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        os.rename(log_file, backup_name)
        print(f"Log rotated: {backup_name}")

    with open(log_file, "a", encoding="utf-8") as file:
        if match_id != 0:
            log_entry = f"{match_id}\n"
            file.write(log_entry)
            log_info(f"Success save disinct_match_id! -> {match_id}")
        else:
            log_entry = f"{USER_NICKNAME+TAG_LINE}\n"
            file.write(log_entry)
            log_info(f"Success save disinct_nickname! -> {USER_NICKNAME+TAG_LINE}")

# check 관리 함수
def manage_check(file_path, check):
    with open(file_path, 'r', encoding='UTF8') as f:
        data = f.readlines()
        for d in data:
            check[d] = True

#main
if __name__ == "__main__":
    idx = 156
    check_nickname = defaultdict(bool)
    check_match_id = defaultdict(bool)
    distinct_nickname_path = '/laewon/Riot/logs/distinct_nickname.log'
    distinct_match_id_path = '/laewon/Riot/logs/distinct_match_id.log'

    #Riot API 유효기간 끝 대비
    if idx != 1:
        manage_check(distinct_nickname_path, check_nickname)
        manage_check(distinct_match_id_path, check_match_id)

    # 첫시작 유저 닉네임:태그
    USER_NICKNAME = '현동방'
    TAG_LINE = 'KR1'
    # 중복을 방지하기 위해 nickname 로그 저장
    distinct_something(USER_NICKNAME, TAG_LINE, 0, distinct_nickname_path)

    aram_matches = []
    
    #데이터 저장을 위한 while문
    while True:

        # 현재 닉네임은 확인했다고 판정
        check_nickname[USER_NICKNAME+TAG_LINE] = True
        
        # USER_NICKNAME:TAG_LINE을 가진 소환사의 puuid 얻기
        puuid = get_puuid(USER_NICKNAME, TAG_LINE)
        log_info(f"{USER_NICKNAME}:{TAG_LINE} PUUID retrieved: {puuid}")
        if puuid == False: break

        #if puuid == None:
        #    USER_NICKNAME, TAG_LINE = next_user_name(USER_NICKNAME, TAG_LINE, aram_matches[0], check_nickname)
        #    continue
        
        # USER_NICKNAME:TAG_LINE의 칼바람 match_ids 얻기
        log_info("Fetching match IDs...")
        match_ids = fetch_match_ids(puuid)
        if match_ids == False: break

        # 얻은 match_ids를 통해 각 match_id별 match 정보 얻기
        log_info("Fetching match data...")
        temp_aram_matches = aram_matches[:]
        aram_matches = fetch_match_data(match_ids, check_match_id)
        if aram_matches == False: break


        # match 정보가 없다면
        if len(aram_matches) == 0:
            log_info("Oops There is no data... Change USERNAME")

            # USER_NICKNAME:TAG_LINE을 변경하여 다시 진행
            USER_NICKNAME, TAG_LINE = next_user_name(temp_user_nickname, temp_user_nickname, temp_aram_matches[1], check_nickname)
            continue

        #match 정보가 있다면 json파일로 저장
        save_to_file(aram_matches, f"/laewon/Riot/data/aram_matches-{idx}.json")
        idx+=1
        
        # 현재 USER_NICKNAME, TAG_LINE을 저장해 놓고
        temp_user_nickname = USER_NICKNAME
        temp_user_tag_line = TAG_LINE
        
        # USER_NICKNAME, TAG_LINE은 변경
        USER_NICKNAME, TAG_LINE = next_user_name(USER_NICKNAME, TAG_LINE, aram_matches[0], check_nickname)
