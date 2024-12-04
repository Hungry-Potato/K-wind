from pyspark.ml import PipelineModel
from pyspark.sql import Row
from pyspark.sql.functions import col, udf
from pyspark.sql.types import DoubleType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml import Pipeline
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("model-test") \
    .config("spark.some.config.option", "some-value") \
    .getOrCreate()

model = PipelineModel.load("hdfs://MN:9000/model/random_forest_model")
rf_model = model.stages[-1]

data = [
    Row(
        **{
            'blue c1': 61,
            'blue-c1-tier': 'GOLD III',
            'blue_c1-mastery': 4,
            'blue c2': 235,
            'blue-c2-tier': 'DIAMOND III',
            'blue_c2-mastery': 8,
            'blue c3': 36,
            'blue-c3-tier': 'UNRANK',
            'blue_c3-mastery': 3,
            'blue c4': 163,
            'blue-c4-tier': 'GOLD IV',
            'blue_c4-mastery': 8,
            'blue c5': 27,
            'blue-c5-tier': 'GOLD III',
            'blue_c5-mastery': 2,
            'red c1': 79,
            'red-c1-tier': 'UNRANK',
            'red_c1-mastery': 6,
            'red c2': 82,
            'red-c2-tier': 'PLATINUM IV',
            'red_c2-mastery': 3,
            'red c3': 15,
            'red-c3-tier': 'DIAMOND IV',
            'red_c3-mastery': 1,
            'red c4': 7,
            'red-c4-tier': 'UNRANK',
            'red_c4-mastery': 4,
            'red c5': 268,
            'red-c5-tier': 'DIAMOND III',
            'red_c5-mastery': 4,
            'duration': 35.0
        }
    )
]

new_data_df = spark.createDataFrame(data)
new_data_df.show()

def tier_to_numeric(tier):
    tier_mapping = {
        "IRON I": 0.4, "IRON II": 0.3, "IRON III": 0.2, "IRON IV": 0.1,
        "BRONZE I": 1.3, "BRONZE II": 1.2, "BRONZE III": 1.1, "BRONZE IV": 1.0,
        "SILVER I": 2.3, "SILVER II": 2.2, "SILVER III": 2.1, "SILVER IV": 2.0,
        "GOLD I": 3.3, "GOLD II": 3.2, "GOLD III": 3.1, "GOLD IV": 3.0,
        "PLATINUM I": 4.3, "PLATINUM II": 4.2, "PLATINUM III": 4.1, "PLATINUM IV": 4.0,
        "EMERALD I": 6.9, "EMERALD II": 6.6, "EMERALD III": 6.3, "EMERALD IV": 6.0,
        "DIAMOND I": 9.5, "DIAMOND II": 9, "DIAMOND III": 8.5, "DIAMOND IV": 8.0,
        "MASTER": 10.0, "GRANDMASTER": 15.0, "CHALLENGER": 20.0, "UNRANK": 1.9
    }
    if tier in tier_mapping:
        return tier_mapping[tier]
    else:
        return 0

tier_to_numeric_udf = udf(tier_to_numeric, DoubleType())

for col_name in new_data_df.columns:
    if col_name.endswith('tier'):
        new_data_df = new_data_df.withColumn(col_name, tier_to_numeric_udf(col(col_name)))

numeric_cols = new_data_df.columns

assembler = VectorAssembler(inputCols=numeric_cols, outputCol="features")

pipeline = Pipeline(stages=[assembler])

new_data_df = pipeline.fit(new_data_df).transform(new_data_df)

predictions = rf_model.transform(new_data_df)

def extract_probabilities(probability_vector):
    if probability_vector is not None:
        return float(probability_vector[0]), float(probability_vector[1])
    return None, None

extract_probabilities_udf = udf(extract_probabilities, returnType="struct<blue_win_0: double, blue_win_1: double>")

predictions = predictions.withColumn('probabilities', extract_probabilities_udf(col('probability')))
predictions = predictions.withColumn('blue_win_0', col('probabilities.blue_win_0'))
predictions = predictions.withColumn('blue_win_1', col('probabilities.blue_win_1'))

predictions.select("blue_win_0", "blue_win_1").show(truncate=False)