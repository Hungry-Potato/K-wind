import React, { useState } from "react";
import axios from "axios";
import App1 from './App1';
function App() {
  // 상태 변수 초기화 (blue와 red 항목을 나누어 저장)
  const [formData, setFormData] = useState({
    "blue c1": "", "blue c1-tier": "", "blue c1-mastery": "",
    "blue c2": "", "blue c2-tier": "", "blue c2-mastery": "",
    "blue c3": "", "blue c3-tier": "", "blue c3-mastery": "",
    "blue c4": "", "blue c4-tier": "", "blue c4-mastery": "",
    "blue c5": "", "blue c5-tier": "", "blue c5-mastery": "",
    "red c1": "", "red c1-tier": "", "red c1-mastery": "",
    "red c2": "", "red c2-tier": "", "red c2-mastery": "",
    "red c3": "", "red c3-tier": "", "red c3-mastery": "",
    "red c4": "", "red c4-tier": "", "red c4-mastery": "",
    "red c5": "", "red c5-tier": "", "red c5-mastery": "",
  });

  const [generatedData, setGeneratedData] = useState(null);  // 데이터 출력용 상태
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  // state 설정: 버튼 클릭 여부를 관리
  const [showApp1, setShowApp1] = useState(true);

  const handleButtonClick = () => {
    setShowApp1(!showApp1);
  };
  const tierOptions = [
    "IRON I", "IRON II", "IRON III", "IRON IV",
    "BRONZE I", "BRONZE II", "BRONZE III", "BRONZE IV",
    "SILVER I", "SILVER II", "SILVER III", "SILVER IV",
    "GOLD I", "GOLD II", "GOLD III", "GOLD IV",
    "PLATINUM I", "PLATINUM II", "PLATINUM III", "PLATINUM IV",
    "EMERALD I", "EMERALD II", "EMERALD III", "EMERALD IV",
    "DIAMOND I", "DIAMOND II", "DIAMOND III", "DIAMOND IV",
    "MASTER I", "GRANDMASTER I", "CHALLENGER I", "UNRANK"
  ];
 const x = {
    "Aatrox": 266, "Ahri": 103, "Akali": 84, "Akshan": 166, "Alistar": 12, "Ambessa": 799,
    "Amumu": 32, "Anivia": 34, "Annie": 1, "Aphelios": 523, "Ashe": 22, "Aurelion Sol": 136,
    "Aurora": 893, "Azir": 268, "Bard": 432, "Bel'Veth": 200, "Blitzcrank": 53, "Brand": 63,
    "Braum": 201, "Briar": 233, "Caitlyn": 51, "Camille": 164, "Cassiopeia": 69, "Cho'Gath": 31,
    "Corki": 42, "Darius": 122, "Diana": 131, "Draven": 119, "Dr. Mundo": 36, "Ekko": 245,
    "Elise": 60, "Evelynn": 28, "Ezreal": 81, "Fiddlesticks": 9, "Fiora": 114, "Fizz": 105,
    "Galio": 3, "Gangplank": 41, "Garen": 86, "Gnar": 150, "Gragas": 79, "Graves": 104,
    "Gwen": 887, "Hecarim": 120, "Heimerdinger": 74, "Hwei": 910, "Illaoi": 420, "Irelia": 39,
    "Ivern": 427, "Janna": 40, "Jarvan IV": 59, "Jax": 24, "Jayce": 126, "Jhin": 202, "Jinx": 222,
    "Kai'Sa": 145, "Kalista": 429, "Karma": 43, "Karthus": 30, "Kassadin": 38, "Katarina": 55,
    "Kayle": 10, "Kayn": 141, "Kennen": 85, "Kha'Zix": 121, "Kindred": 203, "Kled": 240,
    "Kog'Maw": 96, "K'Sante": 897, "LeBlanc": 7, "Lee Sin": 64, "Leona": 89, "Lillia": 876,
    "Lissandra": 127, "Lucian": 236, "Lulu": 117, "Lux": 99, "Malphite": 54, "Malzahar": 90,
    "Maokai": 57, "Master Yi": 11, "Milio": 902, "Miss Fortune": 21, "Wukong": 62, "Mordekaiser": 82,
    "Morgana": 25, "Naafiri": 950, "Nami": 267, "Nasus": 75, "Nautilus": 111, "Neeko": 518,
    "Nidalee": 76, "Nilah": 895, "Nocturne": 56, "Nunu & Willump": 20, "Olaf": 2, "Orianna": 61,
    "Ornn": 516, "Pantheon": 80, "Poppy": 78, "Pyke": 555, "Qiyana": 246, "Quinn": 133, "Rakan": 497,
    "Rammus": 33,"Rek'Sai": 421, "Rell": 526, "Renata Glasc": 888, "Renekton": 58, "Rengar": 107,
    "Riven": 92, "Rumble": 68, "Ryze": 13, "Samira": 360, "Sejuani": 113, "Senna": 235, "Seraphine": 147,
    "Sett": 875, "Shaco": 35, "Shen": 98, "Shyvana": 102, "Singed": 27, "Sion": 14, "Sivir": 15, "Skarner": 72,
    "Smolder": 901, "Sona": 37, "Soraka": 16, "Swain": 50, "Sylas": 517, "Syndra": 134, "Tahm Kench": 223,
    "Taliyah": 163, "Talon": 91, "Taric": 44, "Teemo": 17, "Thresh": 412, "Tristana": 18, "Trundle": 48,
    "Tryndamere": 23, "Twisted Fate": 4, "Twitch": 29, "Udyr": 77, "Urgot": 6, "Varus": 110, "Vayne": 67,
    "Veigar": 45, "Vel'Koz": 161, "Vex": 711, "Vi": 254, "Viego": 234, "Viktor": 112, "Vladimir": 8,
    "Volibear": 106, "Warwick": 19, "Xayah": 498, "Xerath": 101, "Xin Zhao": 5, "Yasuo": 157, "Yone": 777,
    "Yorick": 83, "Yuumi": 350, "Zac": 154, "Zed": 238, "Zeri": 221, "Ziggs": 115, "Zilean": 26, "Zoe": 142,
    "Zyra": 143
 };

 const champions = [
    "Aatrox", "Ahri", "Akali", "Akshan", "Alistar", "Ambessa", "Amumu", "Anivia",
    "Annie", "Aphelios", "Ashe", "Aurelion Sol", "Aurora", "Azir", "Bard", "Bel'Veth",
    "Blitzcrank", "Brand", "Braum", "Briar", "Caitlyn", "Camille", "Cassiopeia", "Cho'Gath",
    "Corki", "Darius", "Diana", "Draven", "Dr. Mundo", "Ekko", "Elise", "Evelynn",
    "Ezreal", "Fiddlesticks", "Fiora", "Fizz", "Galio", "Gangplank", "Garen", "Gnar",
    "Gragas", "Graves", "Gwen", "Hecarim", "Heimerdinger", "Hwei", "Illaoi", "Irelia",
    "Ivern", "Janna", "Jarvan IV", "Jax", "Jayce", "Jhin", "Jinx", "Kai'Sa",
    "Kalista", "Karma", "Karthus", "Kassadin", "Katarina", "Kayle", "Kayn", "Kennen",
    "Kha'Zix", "Kindred", "Kled", "Kog'Maw", "K'Sante", "LeBlanc", "Lee Sin", "Leona",
    "Lillia", "Lissandra", "Lucian", "Lulu", "Lux", "Malphite", "Malzahar", "Maokai",
    "Master Yi", "Milio", "Miss Fortune", "Wukong", "Mordekaiser", "Morgana", "Naafiri", "Nami",
    "Nasus", "Nautilus", "Neeko", "Nidalee", "Nilah", "Nocturne", "Nunu & Willump", "Olaf",
    "Orianna", "Ornn", "Pantheon", "Poppy", "Pyke", "Qiyana", "Quinn", "Rakan",
    "Rammus", "Rek'Sai", "Rell", "Renata Glasc", "Renekton", "Rengar", "Riven", "Rumble",
    "Ryze", "Samira", "Sejuani", "Senna", "Seraphine", "Sett", "Shaco", "Shen",
    "Shyvana", "Singed", "Sion", "Sivir", "Skarner", "Smolder", "Sona", "Soraka",
    "Swain", "Sylas", "Syndra", "Tahm Kench", "Taliyah", "Talon", "Taric", "Teemo",
    "Thresh", "Tristana", "Trundle", "Tryndamere", "Twisted Fate", "Twitch", "Udyr", "Urgot",
    "Varus", "Vayne", "Veigar", "Vel'Koz", "Vex", "Vi", "Viego", "Viktor",
    "Vladimir", "Volibear", "Warwick", "Xayah", "Xerath", "Xin Zhao", "Yasuo", "Yone",
    "Yorick", "Yuumi", "Zac", "Zed", "Zeri", "Ziggs", "Zilean", "Zoe",
    "Zyra"
];

  // 폼 데이터 업데이트 함수
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  // 생성된 데이터를 출력하는 함수
  const generateData = () => {
    const requestData = {
      "blue c1": x[formData["blue c1"]] !== undefined ? x[formData["blue c1"]] : (formData["blue c1"] === "" ? "" : Number(formData["blue c1"])),
      "blue-c1-tier": formData["blue c1-tier"],
      "blue_c1-mastery": formData["blue c1-mastery"] === "" ? "" : Number(formData["blue c1-mastery"]),
      "blue c2": x[formData["blue c2"]] !== undefined ? x[formData["blue c2"]] : (formData["blue c2"] === "" ? "" : Number(formData["blue c2"])),
      "blue-c2-tier": formData["blue c2-tier"],
      "blue_c2-mastery": formData["blue c2-mastery"] === "" ? "" : Number(formData["blue c2-mastery"]),
      "blue c3": x[formData["blue c3"]] !== undefined ? x[formData["blue c3"]] : (formData["blue c3"] === "" ? "" : Number(formData["blue c3"])),
      "blue-c3-tier": formData["blue c3-tier"],
      "blue_c3-mastery": formData["blue c3-mastery"] === "" ? "" : Number(formData["blue c3-mastery"]),
      "blue c4": x[formData["blue c4"]] !== undefined ? x[formData["blue c4"]] : (formData["blue c4"] === "" ? "" : Number(formData["blue c4"])),
      "blue-c4-tier": formData["blue c4-tier"],
      "blue_c4-mastery": formData["blue c4-mastery"] === "" ? "" : Number(formData["blue c4-mastery"]),
      "blue c5": x[formData["blue c5"]] !== undefined ? x[formData["blue c5"]] : (formData["blue c5"] === "" ? "" : Number(formData["blue c5"])),
      "blue-c5-tier": formData["blue c5-tier"],
      "blue_c5-mastery": formData["blue c5-mastery"] === "" ? "" : Number(formData["blue c5-mastery"]),
      "red c1": x[formData["red c1"]] !== undefined ? x[formData["red c1"]] : (formData["red c1"] === "" ? "" : Number(formData["red c1"])),
      "red-c1-tier": formData["red c1-tier"],
      "red_c1-mastery": formData["red c1-mastery"] === "" ? "" : Number(formData["red c1-mastery"]),
      "red c2": x[formData["red c2"]] !== undefined ? x[formData["red c2"]] : (formData["red c2"] === "" ? "" : Number(formData["red c2"])),
      "red-c2-tier": formData["red c2-tier"],
      "red_c2-mastery": formData["red c2-mastery"] === "" ? "" : Number(formData["red c2-mastery"]),
      "red c3": x[formData["red c3"]] !== undefined ? x[formData["red c3"]] : (formData["red c3"] === "" ? "" : Number(formData["red c3"])),
      "red-c3-tier": formData["red c3-tier"],
      "red_c3-mastery": formData["red c3-mastery"] === "" ? "" : Number(formData["red c3-mastery"]),
      "red c4": x[formData["red c4"]] !== undefined ? x[formData["red c4"]] : (formData["red c4"] === "" ? "" : Number(formData["red c4"])),
      "red-c4-tier": formData["red c4-tier"],
      "red_c4-mastery": formData["red c4-mastery"] === "" ? "" : Number(formData["red c4-mastery"]),
      "red c5": x[formData["red c5"]] !== undefined ? x[formData["red c5"]] : (formData["red c5"] === "" ? "" : Number(formData["red c5"])),
      "red-c5-tier": formData["red c5-tier"],
      "red_c5-mastery": formData["red c5-mastery"] === "" ? "" : Number(formData["red c5-mastery"]),
      // duration은 자동으로 20으로 설정
      duration: 20,
    };

    //setGeneratedData(requestData);
    sendGeneratedDataToAPI(requestData);
  };

  const sendGeneratedDataToAPI = async (data) => {
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const response = await axios.post(
        "http://10.14.30.77:5000/predict1",
        data,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      setResult(response.data); // API 응답을 결과로 설정
    } catch (err) {
      setError(
        err.response?.data?.error ||
        err.message ||
        err.response?.statusText ||
        "Something went wrong"
      );
      console.error("Error details:", err); // 콘솔에 에러 세부 정보 출력
    } finally {
      setLoading(false);
    }
  };
  const formatResult = (result) => {
    if (!result || result.length === 0) return null;

    // Blue와 Red의 승리 확률 추출
    const blueWinProbability = result[0].blue_win_1 * 100;
    const redWinProbability = result[0].blue_win_0 * 100;

    return (
      <div>
        <h3>Prediction Result:</h3>
        <p style={{ color: "blue", fontWeight: "bold" }}>
          Blue가 이길 확률: {blueWinProbability.toFixed(2)}%
        </p>
        <p style={{ color: "red", fontWeight: "bold" }}>
          Red가 이길 확률: {redWinProbability.toFixed(2)}%
        </p>
        {/* 승리 확률을 시각적으로 보여주는 부분 */}
        <div>
          <div
            style={{
              backgroundColor: "blue",
              height: "20px",
              width: `${blueWinProbability}%`,
              borderRadius: "5px",
              marginBottom: "10px",
            }}
          />
          <div
            style={{
              backgroundColor: "red",
              height: "20px",
              width: `${redWinProbability}%`,
              borderRadius: "5px",
            }}
          />
        </div>
      </div>
    );
  };

  return (
    <div style={{ maxWidth: "1200px", margin: "auto", padding: "20px" }}>
      <h1>직접 데이터로 주기</h1>

      <form onSubmit={(e) => e.preventDefault()} style={{ display: "flex", gap: "20px" }}>
        {/* blue 항목 */}
        <div style={{ flex: 1, padding: "20px", borderRight: "2px solid #ccc" }}>
          <h2>Blue Stats</h2>
          {["c1", "c2", "c3", "c4", "c5"].map((num) => (
            <div key={num} style={{ display: "flex", gap: "10px", marginBottom: "10px" }}>
              {/* 각 항목 그룹 */}
              <div style={{ flex: 1 }}>
                <label>{`Blue ${num}:`}</label>
                <select
                        name={`blue ${num}`}
                        value={formData[`blue ${num}`]}
                        onChange={handleInputChange}
                        required
                         style={{ width: "100%" }}
                >
                <option value="">Select Champion</option>
                 {champions.map((champion, index) => (
                        <option key={index} value={champion}>
                                {champion}
                </option>
                  ))}
                </select>

              </div>
              <div style={{ flex: 1 }}>
                <label>{`Blue ${num}-tier:`}</label>
                <select
                  name={`blue ${num}-tier`}
                  value={formData[`blue ${num}-tier`]}
                  onChange={handleInputChange}
                  required
                  style={{ width: "100%" }}
                >
                  <option value="">Select Tier</option>
                  {tierOptions.map((tier, index) => (
                    <option key={index} value={tier}>
                      {tier}
                    </option>
                  ))}
                </select>
              </div>
              <div style={{ flex: 1 }}>
                <label>{`Blue ${num}-mastery:`}</label>
                <input
                  type="number"
                  name={`blue ${num}-mastery`}
                  value={formData[`blue ${num}-mastery`]}
                  onChange={handleInputChange}
                  required
                  style={{ width: "100%" }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* red 항목 */}
        <div style={{ flex: 1, padding: "20px" }}>
          <h2>Red Stats</h2>
          {["c1", "c2", "c3", "c4", "c5"].map((num) => (
            <div key={num} style={{ display: "flex", gap: "10px", marginBottom: "10px" }}>
              {/* 각 항목 그룹 */}
              <div style={{ flex: 1 }}>
              <label>{`Red ${num}:`}</label>
              <select
                name={`red ${num}`}
                value={formData[`red ${num}`]}
                onChange={handleInputChange}
                required
                style={{ width: "100%" }}
              >
                <option value="">Select Champion</option>
                {champions.map((champion, index) => (
                        <option key={index} value={champion}>
                                {champion}
                        </option>
                ))}
              </select>
              </div>
              <div style={{ flex: 1 }}>
                <label>{`Red ${num}-tier:`}</label>
                <select
                  name={`red ${num}-tier`}
                  value={formData[`red ${num}-tier`]}
                  onChange={handleInputChange}
                  required
                  style={{ width: "100%" }}
                >
                  <option value="">Select Tier</option>
                  {tierOptions.map((tier, index) => (
                    <option key={index} value={tier}>
                      {tier}
                    </option>
                  ))}
                </select>
              </div>
              <div style={{ flex: 1 }}>
                <label>{`Red ${num}-mastery:`}</label>
                <input
                  type="number"
                  name={`red ${num}-mastery`}
                  value={formData[`red ${num}-mastery`]}
                  onChange={handleInputChange}
                  required
                  style={{ width: "100%" }}
                />
              </div>
            </div>
          ))}
        </div>
      </form>

       <button
          onClick={generateData}
          type="submit"
          style={{
            background: "blue",
            color: "white",
            padding: "10px 20px",
            border: "none",
            cursor: "pointer",
          }}
        >
          Submit
        </button>
      {/* API 요청 후 결과 출력 */}
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {formatResult(result)}
      
      <br></br>
      <br></br>
      <br></br>
      <br></br>

      <h1>진행중인 게임으로 확인하기</h1>
      {/*<button onClick={handleButtonClick}>
        {showApp1 ? 'Hide' : 'Show'} 진행중인 게임
      </button>*/}
      {showApp1 && <App1 />}  {/* showApp1이 true일 때만 App1 렌더링 */}
    </div>
  );
}

export default App;
