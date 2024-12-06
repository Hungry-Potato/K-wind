import os
import pandas as pd
import json
import subprocess
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# JSON 데이터를 읽고 처리된 상태 기록
def read_and_process_json():
    file_path = '/laewon/Riot/data'  # JSON 파일 경로
    processed_files_path = '/laewon/Riot/logs/processed_files.txt'  # 처리된 파일 기록 경로

    # 처리된 파일 목록 읽기
    if os.path.exists(processed_files_path):
        with open(processed_files_path, 'r') as f:
            processed_files = set(f.read().splitlines())
    else:
        processed_files = set()

    # 현재 디렉토리의 모든 JSON 파일 가져오기
    all_files = [f for f in os.listdir(file_path) if f.endswith('.json')]
    new_files = [f for f in all_files if f not in processed_files]  # 새 파일만 선택

    if not new_files:
        print("No new JSON files to process.")
        return None

    all_dataframes = []  # 통합 데이터프레임 리스트

    for file in new_files:
        local_path = os.path.join(file_path, file)
        with open(local_path, 'r') as f:
            data = json.load(f)
    
        result = defaultdict(list)

        for match in data:
            participants = match['info']['participants']
            blue_team = [p for p in participants if p['teamId'] == 100]
            red_team = [p for p in participants if p['teamId'] == 200]

            blue_champ_list = []
            red_champ_list = []
    
            for i, p in enumerate(blue_team):
                result[f"blue c{i+1}"].append(p["championId"])
                result[f"blue-c{i+1}-tier"].append(p["tier"])
                result[f"blue_c{i+1}-mastery"].append(p["championMasteryLevel"])
                blue_champ_list.append(p["championId"])
            result[f"blue_team_comb"].append(blue_champ_list)

            for i, p in enumerate(red_team):
                result[f"red c{i+1}"].append(p["championId"])
                result[f"red-c{i+1}-tier"].append(p["tier"])
                result[f"red_c{i+1}-mastery"].append(p["championMasteryLevel"])
                red_champ_list.append(p["championId"])
            result[f"red_team_comb"].append(red_champ_list)
            result["blue_win"].append(blue_team[0]["win"])
            result["duration"].append(match['info']['gameDuration'] / 60)

        df = pd.DataFrame(result)
        all_dataframes.append(df)  # 새 데이터프레임을 리스트에 추가

        # 처리 완료된 파일 기록
        with open(processed_files_path, 'a') as f:
            f.write(file + '\n')

    # 여러 데이터프레임을 하나로 병합
    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)
        final_df.to_csv("match_data_combined.csv", index=False)  # CSV 파일로 저장
        print("All new JSON files have been processed and saved as 'match_data_combined.csv'.")
        return final_df
    else:
        print("No data to merge.")
        return None

# CSV 파일 생성
def create_csv_1(data):
    csv_path = '/tmp/match_data.csv'  # 첫 번째 CSV 저장 경로
    if data:
        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False)
        print(f"1.csv created at {csv_path}")
    else:
        print("No data for 1.csv")

def create_csv_2(data):
    csv_path = '/tmp/2.csv'  # 두 번째 CSV 저장 경로
    if data:
        # 다른 방식으로 데이터 변형 예시
        df = pd.DataFrame(data)
        df['value_squared'] = df['value'] ** 2  # 값의 제곱을 추가
        df.to_csv(csv_path, index=False)
        print(f"2.csv created at {csv_path}")
    else:
        print("No data for 2.csv")

# HDFS 업로드
def upload_to_hdfs_1():
    local_csv = '/tmp/1.csv'
    hdfs_path = '/user/hdfs/Riot/data/1.csv'
    try:
        subprocess.run(['hdfs', 'dfs', '-put', '-f', local_csv, hdfs_path], check=True)
        print(f"1.csv uploaded to HDFS: {hdfs_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to upload 1.csv to HDFS: {e}")

def upload_to_hdfs_2():
    local_csv = '/tmp/2.csv'
    hdfs_path = '/user/hdfs/Riot/data/2.csv'
    try:
        subprocess.run(['hdfs', 'dfs', '-put', '-f', local_csv, hdfs_path], check=True)
        print(f"2.csv uploaded to HDFS: {hdfs_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to upload 2.csv to HDFS: {e}")

# DAG 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'json_to_two_csv_hdfs',
    default_args=default_args,
    description='Process JSON to create two CSV files and upload them to HDFS',
    schedule_interval=timedelta(minutes=10),
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    # JSON 읽기 및 처리
    read_task = PythonOperator(
        task_id='read_and_process_json',
        python_callable=read_and_process_json,
    )

    # CSV 파일 생성
    create_csv_1_task = PythonOperator(
        task_id='create_csv_1',
        python_callable=create_csv_1,
        op_args=["{{ task_instance.xcom_pull(task_ids='read_and_process_json') }}"],
    )

    create_csv_2_task = PythonOperator(
        task_id='create_csv_2',
        python_callable=create_csv_2,
        op_args=["{{ task_instance.xcom_pull(task_ids='read_and_process_json') }}"],
    )

    # HDFS 업로드
    upload_csv_1_task = PythonOperator(
        task_id='upload_to_hdfs_1',
        python_callable=upload_to_hdfs_1,
    )

    upload_csv_2_task = PythonOperator(
        task_id='upload_to_hdfs_2',
        python_callable=upload_to_hdfs_2,
    )

    # 작업 순서 정의
    read_task >> [create_csv_1_task, create_csv_2_task]
    create_csv_1_task >> upload_csv_1_task
    create_csv_2_task >> upload_csv_2_task
