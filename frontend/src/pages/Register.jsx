import { useState } from "react";
import api from "../api/api";

export default function Register({ onSwitch }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();

    if (password !== confirm) {
      alert("Passwords do not match");
      return;
    }

    try {
      setLoading(true);

      await api.post("/register", {
        username,
        password,
      });

      alert("Account created. Please login.");
      onSwitch();
    } catch (err) {
      alert(
        err.response?.data?.error || "Registration failed"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-bg" />
      <div className="auth-orb one" />
      <div className="auth-orb two" />

      <form className="auth-card" onSubmit={handleRegister}>
        <div className="auth-title">🌾 Create account</div>
        <div className="auth-sub">
          Start diagnosing crops with AI
        </div>

        <div className="auth-field">
          <input
            placeholder=" "
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <label>Username</label>
        </div>

        <div className="auth-field">
          <input
            type="password"
            placeholder=" "
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <label>Password</label>
        </div>

        <div className="auth-field">
          <input
            type="password"
            placeholder=" "
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            required
          />
          <label>Confirm password</label>
        </div>

        <button className="auth-btn" disabled={loading}>
          {loading ? "Creating..." : "Register"}
        </button>

        <div
          className="auth-link"
          onClick={onSwitch}
        >
          Back to login
        </div>
      </form>
    </div>
  );
}
