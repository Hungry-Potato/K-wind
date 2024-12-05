from flask import Flask, request, jsonify
from pyspark.ml import PipelineModel
from pyspark.sql import Row
from pyspark.sql.functions import col, udf
from pyspark.sql.types import DoubleType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml import Pipeline
from pyspark.sql import SparkSession
from urllib import parse
import requests

app = Flask(__name__)

spark = SparkSession.builder \
    .appName("model-test") \
    .config("spark.some.config.option", "some-value") \
    .getOrCreate()

API_KEY = ''
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": API_KEY
}


model = PipelineModel.load("hdfs://MN:9000/model/random_forest_model")
rf_model = model.stages[-1]

tier_mapping = {
    "IRON I": 0.4, "IRON II": 0.3, "IRON III": 0.2, "IRON IV": 0.1,
    "BRONZE I": 1.3, "BRONZE II": 1.2, "BRONZE III": 1.1, "BRONZE IV": 1.0,
    "SILVER I": 2.3, "SILVER II": 2.2, "SILVER III": 2.1, "SILVER IV": 2.0,
    "GOLD I": 3.3, "GOLD II": 3.2, "GOLD III": 3.1, "GOLD IV": 3.0,
    "PLATINUM I": 4.3, "PLATINUM II": 4.2, "PLATINUM III": 4.1, "PLATINUM IV": 4.0,
    "EMERALD I": 6.9, "EMERALD II": 6.6, "EMERALD III": 6.3, "EMERALD IV": 6.0,
    "DIAMOND I": 9.5, "DIAMOND II": 9, "DIAMOND III": 8.5, "DIAMOND IV": 8.0,
    "MASTER I": 10.0, "GRANDMASTER I": 15.0, "CHALLENGER I": 20.0, "UNRANK": 1.9
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
            print(f"Error fetching match IDs: {e}. Break")
            return False

def get_mastery(puuid, c_id):
    url = f"https://kr.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{c_id}"

    while True:
        try:
            response = requests.get(url, headers=REQUEST_HEADERS)
            response.raise_for_status()
            response_data = response.json()
            
            return response_data['championLevel']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return 1
        
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
        
        puuid = match_data['participants'][i]['puuid']
        ci = match_data['participants'][i]['championId']
        
        champion_mastery = get_mastery(puuid, ci)
        match_data['participants'][i]['championMasteryLevel'] = champion_mastery
        
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
    
    return result

def tier_to_numeric(tier):
    return tier_mapping.get(tier, 0)

def get_predictions(input_data):
    if isinstance(input_data, dict):
        input_data = [input_data]
    
    rows = [Row(**item) for item in input_data]
    
    spark_df = spark.createDataFrame(rows)
    
    for col_name in spark_df.columns:
        if col_name.endswith('tier'):
            spark_df = spark_df.withColumn(col_name, tier_to_numeric_udf(col(col_name)))
    
    numeric_cols = spark_df.columns
    assembler = VectorAssembler(inputCols=numeric_cols, outputCol = 'features')
    pipeline = Pipeline(stages = [assembler])
    spark_df = pipeline.fit(spark_df).transform(spark_df)
    
    predictions = rf_model.transform(spark_df)
    
    return predictions

def get_probabilities(predictions):
    def extract_probabilities(v):
        if v is not None:
            return float(v[0]), float(v[1])
        return None, None
    
    extract_probabilities_udf = udf(extract_probabilities, returnType="struct<blue_win_0: double, blue_win_1: double>")
    predictions = predictions.withColumn('probabilities', extract_probabilities_udf(col('probability')))
    predictions = predictions.withColumn('blue_win_0', col('probabilities.blue_win_0'))
    predictions = predictions.withColumn('blue_win_1', col('probabilities.blue_win_1'))

    return predictions.select("blue_win_0", "blue_win_1").toPandas().to_dict(orient="records")

tier_to_numeric_udf = udf(tier_to_numeric, DoubleType())

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    nickname = data.get('nickname')
    tagline = data.get('tagline')
    
    puuid = get_puuid(nickname, tagline)
    
    if not puuid:
        return jsonify({"error": "Invalid Nickname or Tagline"}), 400
    
    match_data = get_match_data(puuid)
    if not match_data:
        return jsonify({"error": "No active match found"}), 404
    
    processed_data = fetch_match_data(match_data)
    
    result = change_data(processed_data, {})
    
    predictions = get_predictions(result)

    probabilities = get_probabilities(predictions)
   
    return jsonify(probabilities)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5000)
            
