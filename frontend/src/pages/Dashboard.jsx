import { useEffect, useState } from "react";
import api from "../api/api";
import AudioRecorder from "../components/AudioRecorder";

export default function Dashboard({
  imageFile,
  setImageId,
  setDisease,
  setConfidence,
  setLoadingAnalyze,
  imageId,
  disease,
  confidence
}) {

  const [language, setLanguage] = useState("en-IN");
  const [question, setQuestion] = useState("");
  const [loadingAsk, setLoadingAsk] = useState(false);
  const [history, setHistory] = useState([]);

  /* -----------------------------
     Analyze image automatically
  ------------------------------*/
  useEffect(() => {
    if (!imageFile) return;
    analyzeImage();
    // eslint-disable-next-line
  }, [imageFile]);

  const analyzeImage = async () => {
    try {
      setLoadingAnalyze(true);

      const formData = new FormData();
      formData.append("image", imageFile);
      formData.append("language", language);

      const res = await api.post("/plant/analyze", formData);

      setImageId(res.data.image_id);
      setDisease(res.data.disease);
      setConfidence(res.data.confidence);

    } catch (e) {
      alert("Failed to analyze image");
      return;
    } finally {
      setLoadingAnalyze(false);
    }

    // load history should NOT break analyze flow
    try {
      await loadHistory();
    } catch (e) {
      console.error("History failed to load after analyze");
    }
  };

  /* -----------------------------
     Ask by text
  ------------------------------*/
  const askByText = async () => {
    if (!question.trim()) return;

    try {
      setLoadingAsk(true);

      await api.post(
        "/plant/ask",
        {
          question,
          language
        },
        {
          headers: {
            "Content-Type": "application/json"
          },
          responseType: "blob"
        }
      );

      setQuestion("");

    } catch (e) {
      alert("Failed to ask question");
      return;
    } finally {
      setLoadingAsk(false);
    }

    // history must not break asking
    try {
      await loadHistory();
    } catch (e) {
      console.error("History failed to load after ask");
    }
  };

  /* -----------------------------
     Load backend history
  ------------------------------*/
  const loadHistory = async () => {
    const res = await api.get("/plant/history");
    setHistory(res.data);
  };

  const currentImageHistory =
    history.find((h) => h.image_id === imageId)?.qa_history || [];

  /* -----------------------------
     UI
  ------------------------------*/
  return (
    <div className="dash-right">

      {/* Language */}
      <div className="lang-row">
        <span>Language</span>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
        >
          <option value="en-IN">English</option>
          <option value="te-IN">తెలుగు</option>
          <option value="hi-IN">हिन्दी</option>
        </select>
      </div>

      {imageId && (
        <div className="ask-card">

          <textarea
            placeholder="Ask your question…"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />

          <div className="ask-actions">
            <button onClick={askByText} disabled={loadingAsk}>
              {loadingAsk ? "Asking..." : "Send"}
            </button>

            <AudioRecorder
              language={language}
            />
          </div>

        </div>
      )}

      {imageId && (
        <div className="qa-list">

          <h4>Last questions for this image</h4>

          {currentImageHistory.length === 0 && (
            <div className="muted">No questions yet</div>
          )}

          {currentImageHistory.map((qa, i) => (
            <div className="qa-card" key={i}>
              <div className="qa-q">{qa.question}</div>
              <div className="qa-a">{qa.answer}</div>
            </div>
          ))}

        </div>
      )}

    </div>
  );
}
