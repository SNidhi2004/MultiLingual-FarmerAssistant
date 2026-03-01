import { useState, useEffect } from "react";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import "./index.css";
import Sidebar from "./components/Sidebar";
import ImagePanel from "./components/ImagePanel";

export default function App() {
  const [page, setPage] = useState("login");
  const [token, setToken] = useState(localStorage.getItem("token"));

  // image workflow state (moved up from Dashboard)

const [imageFile, setImageFile] = useState(null);
const [imagePreview, setImagePreview] = useState(null);

const [imageId, setImageId] = useState(null);
const [disease, setDisease] = useState(null);
const [confidence, setConfidence] = useState(null);

const [loadingAnalyze, setLoadingAnalyze] = useState(false);

  const resetCurrent = () => {
  setImageFile(null);
  setImagePreview(null);
  setImageId(null);
  setDisease(null);
  setConfidence(null);
};

  useEffect(() => {
  if (token) {
    setPage("dashboard");
  } else {
    setPage("login");
  }
}, [token]);


//   {page === "login" && (
//   <Login
//     onSuccess={() => setPage("dashboard")}
//     onSwitch={() => setPage("register")}
//   />
// )}

// {page === "register" && (
//   <Register
//     onSwitch={() => setPage("login")}
//   />
// )}


  return (
  <>
    {page === "login" && (
      <Login
        onSuccess={() => {
          setToken(localStorage.getItem("token"));
          setPage("dashboard");
        }}
        onSwitch={() => setPage("register")}
      />
    )}

    {page === "register" && (
      <Register
        onSwitch={() => setPage("login")}
      />
    )}

    {page === "dashboard" && (
  <div style={{ display: "flex", minHeight: "100vh" }}>

    <Sidebar
      onLogout={() => {
        localStorage.removeItem("token");
        setToken(null);
        setPage("login");
      }}
      onHistory={() => setPage("history")}
    >
      <ImagePanel
  imagePreview={imagePreview}
  setImageFile={setImageFile}
  setImagePreview={setImagePreview}
  resetCurrent={resetCurrent}
  loadingAnalyze={loadingAnalyze}
  disease={disease}
  confidence={confidence}
/>

    </Sidebar>

    <div style={{ flex: 1, padding: 24 }}>
      <Dashboard
  imageFile={imageFile}
  setImageId={setImageId}
  setDisease={setDisease}
  setConfidence={setConfidence}
  setLoadingAnalyze={setLoadingAnalyze}
  imageId={imageId}
  disease={disease}
  confidence={confidence}
/>

    </div>

  </div>
)}

  </>
);

}
