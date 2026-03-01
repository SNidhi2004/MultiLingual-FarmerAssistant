import { useState } from "react";
import api from "../api/api";

export default function Login({ onSuccess, onSwitch }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      setLoading(true);

      const res = await api.post("/login", {
        username,
        password,
      });

      localStorage.setItem("token", res.data.token);

      onSuccess();
    } catch (err) {
      alert(
        err.response?.data?.error || "Login failed"
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

      <form className="auth-card" onSubmit={handleLogin}>
        <div className="auth-title">🌱 Farmer Assistant</div>
        <div className="auth-sub">
          AI support for healthier crops
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

        <button className="auth-btn" disabled={loading}>
          {loading ? "Signing in..." : "Login"}
        </button>

        <div
          className="auth-link"
          onClick={onSwitch}
        >
          Create a new account
        </div>
      </form>
    </div>
  );
}
