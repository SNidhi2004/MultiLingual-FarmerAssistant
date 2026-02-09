import { useState } from "react";
import "./App.css";

const diseaseDatabase = {
  blight: {
    name: "Bacterial Blight",
    symptoms: "Angular leaf spots, yellowing, wilting",
    medicine: "Spray Streptomycin 0.01% + Copper Oxychloride"
  },
  curl: {
    name: "Leaf Curl Disease",
    symptoms: "Upward curling, thickened leaves",
    medicine: "Spray Imidacloprid 0.3 ml/L water"
  },
  spot: {
    name: "Leaf Spot Disease",
    symptoms: "Brown or black circular spots",
    medicine: "Spray Mancozeb 2.5 g/L water"
  },
  healthy: {
    name: "Healthy Plant",
    symptoms: "No visible symptoms",
    medicine: "No medicine required"
  }
};

function detectDiseaseFromImage(fileName) {
  const name = fileName.toLowerCase();

  if (name.includes("blight")) return diseaseDatabase.blight;
  if (name.includes("curl")) return diseaseDatabase.curl;
  if (name.includes("spot")) return diseaseDatabase.spot;

  // Default fallback
  return diseaseDatabase.healthy;
}

function App() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "👋 Upload a cotton leaf image to detect disease." }
  ]);

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const result = detectDiseaseFromImage(file.name);

    setMessages(prev => [
      ...prev,
      { sender: "user", text: `📷 Image uploaded: ${file.name}` },
      { sender: "bot", text: `🦠 **Disease Detected:** ${result.name}` },
      { sender: "bot", text: `📌 **Symptoms:** ${result.symptoms}` },
      { sender: "bot", text: `💊 **Recommended Medicine:** ${result.medicine}` }
    ]);
  };

  return (
    <div className="container">
      <div className="sidebar">
        <h2>🌿 Cotton AI</h2>
        <p>Upload cotton leaf image</p>
        <input type="file" onChange={handleImageUpload} />
      </div>

      <div className="chat">
        {messages.map((msg, i) => (
          <div key={i} className={msg.sender}>
            {msg.text}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
