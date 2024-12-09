from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os
import pandas as pd
import json
from collections import defaultdict


def match_data(data, result):
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

def champion_data(data, champion_dict):
    for match in data:
        participants = match['info']['participants']
        game_duration = match['info']['gameDuration'] / 60
        for p in participants:
            champion_id = p["championId"]
            win = p["win"]
            item0 = p["item0"]
            item1 = p["item1"] 
            item2 = p["item2"] 
            item3 = p["item3"] 
            item4 = p["item4"] 
            item5 = p["item5"] 
            item6 = p["item6"]
            kill = p["kills"]
            death = p["deaths"]
            assist = p["assists"]
            total_damage_to_champion = p["totalDamageDealtToChampions"]
            total_damage_taken = p["totalDamageTaken"]
                
            champion_dict[champion_id].append({
                'game_duration': game_duration,
                'win': win,
                'item0': item0,
                'item1': item1,
                'item2': item2,
                'item3': item3,
                'item4': item4,
                'item5': item5,
                'item6': item6,
                'kill': kill,
                'death': death,
                'assist': assist,
                'total_damage_to_champion': total_damage_to_champion,
                'total_damage_taken': total_damage_taken
            })

    # 각 챔피언별로 CSV 파일을 생성
    for champion_id, matches in champion_dict.items():
        champion_df = pd.DataFrame(matches)

        champion_file_path = os.path.join('/laewon/Riot/output', f"champion_{champion_id}.csv")

        if os.path.exists(champion_file_path):
            existing_df = pd.read_csv(champion_file_path)
            champion_df = pd.concat([existing_df, champion_df], ignore_index=True)

        champion_df.to_csv(champion_file_path, index=False)
        print(f"Champion data for champion {champion_id} saved to {champion_file_path}.")

# JSON 데이터를 읽고 처리된 상태 기록
def read_and_process_json(**kwargs):
    file_path = '/laewon/Riot/data' 
    processed_files_path = '/laewon/Riot/logs/processed_files.txt'
    output_csv = '/laewon/Riot/output/match_data_combined.csv'

    if os.path.exists(processed_files_path):
        with open(processed_files_path, 'r') as f:
            processed_files = set(f.read().splitlines())
    else:
        processed_files = set()


    all_files = [f for f in os.listdir(file_path) if f.endswith('.json')]
    new_files = [f for f in all_files if f not in processed_files]

    if not new_files:
        print("No new JSON files to process.")
        return None

    all_dataframes = []
    champion_dict = defaultdict(list)

    for file in new_files:
        local_path = os.path.join(file_path, file)
        with open(local_path, 'r') as f:
            data = json.load(f)
    
        result = defaultdict(list)
        match_data(data, result)
        df = pd.DataFrame(result)
        all_dataframes.append(df)

        champion_data(data, champion_dict)

        with open(processed_files_path, 'a') as f:
            f.write(file + '\n')

    if os.path.exists(output_csv):
        existing_df = pd.read_csv(output_csv)
        all_dataframes.insert(0, existing_df)


    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)
        final_df.to_csv(output_csv, index=False)
        print("All new JSON files have been processed and saved as 'match_data_combined.csv'.")
        kwargs['ti'].xcom_push(key='output_csv', value=output_csv)
    else:
        print("No data to merge.")
        kwargs['ti'].xcom_push(key='output_csv', value=output_csv)

# Airflow DAG 정의
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'process_and_upload_json_to_hdfs',
    default_args=default_args,
    description='Process JSON files, update CSV, and upload to HDFS',
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2024, 12, 2),
    catchup=False,
)


process_task = PythonOperator(
    task_id='process_json_files',
    python_callable=read_and_process_json,
    provide_context=True,
    dag=dag,
)


save_to_hdfs_task = BashOperator(
    task_id='save_to_hdfs',
    bash_command=(
        'cat "{{ ti.xcom_pull(task_ids=\'process_json_files\', key=\'output_csv\') }}" | '
        'hdfs dfs -put -f /laewon/Riot/output/match_data_combined.csv /data/match_data_combined.csv'
    ),
    dag=dag,
)

save_champion_to_hdfs_task = BashOperator(
    task_id='save_champion_to_hdfs',
    bash_command=(
        'for champion_file in /laewon/Riot/output/champion_*.csv; do '
        '  hdfs dfs -put -f $champion_file /data/$(basename $champion_file); '
        'done'
    ),
    dag=dag,
)

run_make_model_task = BashOperator(
    task_id='run_make_model',
    bash_command='/laewon/spark/bin/spark-submit --master yarn --deploy-mode cluster /laewon/Riot/make_model.py',
    dag=dag,
)

process_task >> save_to_hdfs_task >> save_champion_to_hdfs_task >> run_make_model_task