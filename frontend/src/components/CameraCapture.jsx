import { useEffect, useRef } from "react";

export default function CameraCapture({ onCapture }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: "environment" } })
      .then(stream => (videoRef.current.srcObject = stream))
      .catch(() => alert("Camera not accessible"));
  }, []);

  const capture = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    canvas.toBlob(blob => onCapture(blob), "image/jpeg");
  };

  return (
    <>
      <video ref={videoRef} autoPlay playsInline width="300" />
      <button onClick={capture}>Capture</button>
      <canvas ref={canvasRef} hidden />
    </>
  );
}
