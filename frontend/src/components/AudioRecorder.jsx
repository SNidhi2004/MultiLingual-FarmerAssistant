import { useRef, useState } from "react";
import api from "../api/api";

export default function AudioRecorder({ language }) {
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const streamRef = useRef(null);

  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);

  const playWavBlob = (wavBytes) => {
    const audioBlob = new Blob([wavBytes], { type: "audio/wav" });
    const url = URL.createObjectURL(audioBlob);

    const audio = new Audio(url);
    audio.onended = () => URL.revokeObjectURL(url);
    audio.play();
  };

  const startRecording = async () => {
    if (recording || loading) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = handleStop;

      mediaRecorder.start();
      setRecording(true);

      // auto stop after 5s
      setTimeout(() => {
        if (mediaRecorder.state !== "inactive") {
          mediaRecorder.stop();
        }
      }, 5000);
    } catch (err) {
      console.error("Microphone access error:", err);
      alert("Microphone permission is required.");
    }
  };

  const handleStop = async () => {
    setRecording(false);
    setLoading(true);

    try {
      const blob = new Blob(chunksRef.current, {
        type: "audio/webm",
      });

      const formData = new FormData();
      formData.append("audio", blob);
      formData.append("language", language);

      const res = await api.post("/plant/ask", formData, {
        responseType: "blob",
      });

      playWavBlob(res.data);
    } catch (err) {
      console.error(err);

      // Most common backend issues in your project
      if (err.response?.status === 401) {
        alert("Session expired. Please login again.");
      } else if (err.response) {
        alert("Could not process your voice. Please try again.");
      } else {
        alert("Network error. Please check your connection.");
      }
    } finally {
      setLoading(false);

      // stop mic tracks
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      }
    }
  };

  return (
    <button
  onClick={startRecording}
  disabled={recording || loading}
  className="mic-btn"
>
  {recording
    ? "🎙 Recording..."
    : loading
    ? "Processing..."
    : "🎤 Ask by Voice"}
</button>
  );
}
