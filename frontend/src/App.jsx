import { useState, useRef } from "react";
import "./App.css";
import Login from "./Login";

/* ---------- Disease Data ---------- */
const diseases = [
  {
    en: { name: "Bacterial Blight", med: "Spray Streptomycin 0.01% + Copper Oxychloride" },
    hi: { name: "बैक्टीरियल ब्लाइट", med: "स्ट्रेप्टोमाइसिन 0.01% + कॉपर ऑक्सीक्लोराइड" },
    te: { name: "బాక్టీరియల్ బ్లైట్", med: "స్ట్రెప్టోమైసిన్ 0.01% + కాపర్ ఆక్సీక్లోరైడ్" }
  },
  {
    en: { name: "Leaf Curl Disease", med: "Spray Imidacloprid 0.3 ml/L" },
    hi: { name: "लीफ कर्ल रोग", med: "इमिडाक्लोप्रिड 0.3 मि.ली./ली." },
    te: { name: "లీఫ్ కర్ల్ వ్యాధి", med: "ఇమిడాక్లోప్రిడ్ 0.3 మి.లీ/లీ" }
  },
  {
    en: { name: "Leaf Spot Disease", med: "Spray Mancozeb 2.5 g/L" },
    hi: { name: "लीफ स्पॉट रोग", med: "मैनकोज़ेब 2.5 ग्राम/ली." },
    te: { name: "లీఫ్ స్పాట్ వ్యాధి", med: "మ్యాంకోజెబ్ 2.5 గ్రా/లీ" }
  }
];

function detectDisease(file) {
  const index = (file.size + file.name.length) % diseases.length;
  return diseases[index];
}

/* ---------- SPEAK TOGGLE ---------- */
function toggleSpeak(text, lang) {
  if (speechSynthesis.speaking) {
    speechSynthesis.cancel();
    return;
  }
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = lang === "hi" ? "hi-IN" : lang === "te" ? "te-IN" : "en-US";
  speechSynthesis.speak(utter);
}

export default function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [farmerName, setFarmerName] = useState("");

  const [language, setLanguage] = useState("en");
  const [model, setModel] = useState("YOLOv8");
  const [messages, setMessages] = useState([
    { from: "bot", text: "🌱 Upload cotton leaf image or ask your question." }
  ]);
  const [input, setInput] = useState("");

  const [cameraOn, setCameraOn] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  if (!loggedIn) {
    return (
      <Login
        onLogin={(name) => {
          setFarmerName(name);
          setLoggedIn(true);
        }}
      />
    );
  }

  /* ---------- IMAGE PROCESS ---------- */
  const processImage = (file, label) => {
    const disease = detectDisease(file)[language];
    const confidence = (80 + Math.random() * 15).toFixed(2);

    const response = `Hello ${farmerName},

Disease Detected (${model}):
${disease.name}

Confidence: ${confidence}%

Recommended Medicine:
${disease.med}`;

    setMessages((prev) => [
      ...prev,
      { from: "user", text: label },
      { from: "bot", text: response }
    ]);
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) processImage(file, `📷 Image uploaded: ${file.name}`);
  };

  /* ---------- CAMERA ---------- */
  const openCamera = async () => {
    setCameraOn(true);
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoRef.current.srcObject = stream;
  };

  const closeCamera = () => {
    if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
    }
    setCameraOn(false);
  };

  const capturePhoto = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);

    canvas.toBlob((blob) => {
      const file = new File([blob], "camera.jpg", { type: "image/jpeg" });
      processImage(file, "📸 Photo captured from camera");
    });

    closeCamera();
  };

  /* ---------- VOICE INPUT ---------- */
  const startVoiceInput = () => {
    const recognition = new window.webkitSpeechRecognition();
    recognition.lang =
      language === "hi" ? "hi-IN" :
      language === "te" ? "te-IN" : "en-US";

    recognition.onresult = (e) => {
      setInput(e.results[0][0].transcript);
    };
    recognition.start();
  };

  return (
    <div className="app">
      {/* ---------- SIDEBAR ---------- */}
      <div className="sidebar">
        <h2>🌿 Cotton AI</h2>
        <p>Welcome, {farmerName}</p>

        <label>Language</label>
        <select onChange={(e) => setLanguage(e.target.value)}>
          <option value="en">English</option>
          <option value="hi">Hindi</option>
          <option value="te">Telugu</option>
        </select>

        <label>Model</label>
        <select onChange={(e) => setModel(e.target.value)}>
          <option>YOLOv8</option>
          <option>CNN</option>
          <option>ResNet</option>
        </select>

        <label>Upload Image</label>
        <input type="file" accept="image/*" onChange={handleImageUpload} />

        <button className="camera-btn" onClick={openCamera}>
          📸 Take Photo
        </button>
      </div>

      {/* ---------- CHAT ---------- */}
      <div className="chat-container">
        <div className="chat-box">
          {messages.map((m, i) => (
            <div key={i} className={`msg ${m.from}`}>
              <span>{m.text}</span>
              {m.from === "bot" && (
                <button
                  className="speak-btn"
                  onClick={() => toggleSpeak(m.text, language)}
                >
                  🔊
                </button>
              )}
            </div>
          ))}
        </div>

        {/* ---------- BOTTOM INPUT ---------- */}
        <div className="chat-input">
          <button className="mic-btn" onClick={startVoiceInput}>🎤</button>

          <input
            placeholder="Type or speak your question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />

          <button
            className="send-btn"
            onClick={() => {
              if (!input.trim()) return;
              setMessages((p) => [...p, { from: "user", text: input }]);
              setInput("");
            }}
          >
            Send
          </button>
        </div>
      </div>

      {/* ---------- CAMERA MODAL ---------- */}
      {cameraOn && (
        <div className="camera-modal">
          <div className="camera-box">
            <video ref={videoRef} autoPlay />
            <canvas ref={canvasRef} hidden />

            <div className="camera-actions">
              <button onClick={capturePhoto}>📸 Capture</button>
              <button className="close-btn" onClick={closeCamera}>❌ Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
