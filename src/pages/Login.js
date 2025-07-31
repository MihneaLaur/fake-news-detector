import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setErr("");
    const res = await login(username, password);
    if (res.success) {
      navigate("/dashboard");
    } else {
      setErr(res.message || "Date incorecte!");
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "2rem" }}>
      <h2 style={{ color: "#4f46e5" }}>Login</h2>
      <form className="upload-form" onSubmit={handleLogin} style={{ width: 300 }}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Parolă"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        <button className="main-btn" type="submit">Login</button>
        {err && <div style={{ color: "red", marginTop: 10 }}>{err}</div>}
      </form>
      <span>Nu ai cont? <Link to="/register">Înregistrează-te</Link></span>
    </div>
  );
}