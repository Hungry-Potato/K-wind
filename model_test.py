from flask import Flask, request, jsonify
from pyspark.ml import PipelineModel
from pyspark.sql import Row
from pyspark.sql.functions import col, udf
from pyspark.sql.types import DoubleType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml import Pipeline
from pyspark.sql import SparkSession

app = Flask(__name__)

spark = SparkSession.builder \
    .appName("model-test") \
    .config("spark.some.config.option", "some-value") \
    .getOrCreate()

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

def tier_to_numeric(tier):
    return tier_mapping.get(tier, 0)

tier_to_numeric_udf = udf(tier_to_numeric, DoubleType())

@app.route('/predict', methods=['POST'])
def predict():
    input_data = request.json

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
    
    def extract_probabilities(v):
        if v is not None:
            return float(v[0]), float(v[1])
        return None, None
    
    extract_probabilities_udf = udf(extract_probabilities, returnType="struct<blue_win_0: double, blue_win_1: double>")
    predictions = predictions.withColumn('probabilities', extract_probabilities_udf(col('probability')))
    predictions = predictions.withColumn('blue_win_0', col('probabilities.blue_win_0'))
    predictions = predictions.withColumn('blue_win_1', col('probabilities.blue_win_1'))

    result = predictions.select("blue_win_0", "blue_win_1").toPandas().to_dict(orient="records")
    
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5000)
            
