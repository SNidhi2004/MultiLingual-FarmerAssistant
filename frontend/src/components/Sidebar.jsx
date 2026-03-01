export default function Sidebar({ onLogout, onHistory, children }) {

  return (
    <div
      style={{
        width: "380px",
        minHeight: "100vh",
        padding: "18px 16px",
        background: "linear-gradient(180deg, #0f2027, #203a43)",
        color: "white",
        display: "flex",
        flexDirection: "column",
        gap: "16px"
      }}
    >

      {/* Header */}
      <div>
        <div style={{ fontSize: 20, fontWeight: 700 }}>🌱 Farmer AI</div>
        <div style={{ fontSize: 12, opacity: 0.7 }}>
          Smart crop assistant
        </div>
      </div>

      <button onClick={onHistory} style={btnStyle}>
        📜 History
      </button>

      {/* Image / upload panel goes here */}
      <div style={{ flex: 1, overflowY: "auto" }}>
        {children}
      </div>

      <button
        onClick={onLogout}
        style={{
          ...btnStyle,
          background: "linear-gradient(135deg,#ff6a6a,#ff4757)"
        }}
      >
        🚪 Logout
      </button>
    </div>
  );
}

const btnStyle = {
  padding: "10px 12px",
  borderRadius: "10px",
  border: "none",
  cursor: "pointer",
  fontWeight: 600,
  color: "white",
  background: "linear-gradient(135deg,#00c6ff,#0072ff)",
};
