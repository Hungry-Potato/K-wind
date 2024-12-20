import React, { useState } from "react";
import axios from "axios";

function App1() {
  const [nickname, setNickname] = useState("");
  const [tagline, setTagline] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const response = await axios.post(
        "http://10.14.30.77:5000/predict",
        {
          nickname,
          tagline,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      setResult(response.data);
    } catch (err) {
      setError(
        err.response?.data?.error ||
        err.message ||
        err.response?.statusText ||
        "Something went wrong"
      );
      console.error("Error details:", err);
    } finally {
      setLoading(false);
    }
  };

  const formatResult = (result) => {
    if (!result || result.length === 0) return null;

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
    <div style={{ maxWidth: "600px", margin: "auto", padding: "20px" }}>
      <h1>Nickname & Tagline</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: "20px" }}>
        <div style={{ marginBottom: "10px" }}>
          <label>Nickname:</label>
          <input
            type="text"
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            required
            style={{ width: "100%", padding: "8px", marginTop: "5px" }}
          />
        </div>
        <div style={{ marginBottom: "10px" }}>
          <label>Tagline:</label>
          <input
            type="text"
            value={tagline}
            onChange={(e) => setTagline(e.target.value)}
            required
            style={{ width: "100%", padding: "8px", marginTop: "5px" }}
          />
        </div>
        <button
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
      </form>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {formatResult(result)}
    </div>
  );
}

export default App1;
