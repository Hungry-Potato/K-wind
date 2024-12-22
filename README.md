# K-wind
League of Legend 칼바람나락 승부 예측</br>
[Link]</br>

# 프로젝트 소개
> DataPipeline을 직접 구축해보기 위해 시작된 토이 프로젝트입니다. <br/>
> Hadoop HDFS, SparkML, Airflow의 활용을 목표로 했습니다. <br/>
> 가끔 칼바람을 즐기는데 챔피언 별 조합과 티어만으로도 승률을 예측할 수 있을지 궁금해 토이 프로젝트 주제로 선정했습니다.</br>

# Stack
### App
<table>
  <tr><th rowspan="2">App</th><td>Language</td><td>Python, JavaScript</td>
    <tr><td>API</td><td>Riot API</td>
</table>

### Tools
<table>
	<tr><th rowspan="1">FrontEnd</th><td>React: 18.3.1</td></tr>
	<tr><th rowspan="1">BackEnd</th><td>Flask</td></tr>
  <tr><th rowspan="3">Data Pipeline</th><td>Apache Hadoop: 3.4.0</td></tr>
	<tr><td>Apache Spark: 3.5.1</td></tr>
	<tr><td>Apache Airflow</td></tr>
</table>

<br></br>


# Overall Architecture
![그림1](https://github.com/user-attachments/assets/79229768-1048-49f5-b7c3-ea8a1788f357)

<br></br>

# DataPipeline
## HDFS 데이터 저장
![image](https://github.com/user-attachments/assets/2ad037a6-8996-47f2-8f2e-0e183581c9b2)
![image](https://github.com/user-attachments/assets/c9d3d6e2-e0fc-4206-9aed-ab43bd9674c8)

<br></br>

## 업데이트된 데이터를 기반으로 model 업데이트
![image](https://github.com/user-attachments/assets/7d853b7a-d38e-4088-8d7d-572b6ef2b9a3)

<br></br>

## Airflow DAG
![image](https://github.com/user-attachments/assets/ea3813cb-101f-4e96-aecf-98e8faa6224b)

<br></br>

# 시연

이미 끝난 게임은 예측에 의미가 없다고 생각하여 진행중인 게임 데이터를 통해 예측을 진행합니다.</br>
Input으로는 닉네임과 태그라인을 전달합니다.

![image](https://github.com/user-attachments/assets/9b977ebb-4dbb-4bce-852c-c9a6d10cd3e6)

<br></br>

또한 직접 챔피언, 티어, 챔피언 숙련도를 기입해 예측할 수 있습니다.</br>
아래 데이터는 실제 본인이 플레이한 데이터인데, 실제 결과로도 레드팀이 승리했습니다.

![image](https://github.com/user-attachments/assets/e76a1ce0-f36e-4058-9470-bf1e55f5619a)


---
모델이 항상 정확하지만은 않기 때문에 재미로 보는게 좋을 것 같습니다😊

