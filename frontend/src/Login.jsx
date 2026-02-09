import { useState } from "react";
import "./App.css";

export default function Login({ onLogin }) {
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");

  return (
    <div className="login-wrapper">
      <div className="login-page">
        <div className="login-card">
          <h2>🌱 Cotton Disease Detection</h2>
          <p>Farmer Login</p>

          <input
            type="text"
            placeholder="Farmer Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <input
            type="tel"
            placeholder="Mobile Number"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />

          <button
            onClick={() => {
              if (!name || !phone) {
                alert("Please enter all details");
                return;
              }
              onLogin(name);
            }}
          >
            Login
          </button>
        </div>
      </div>
    </div>
  );
}
