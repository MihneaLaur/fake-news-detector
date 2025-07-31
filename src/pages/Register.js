import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../AuthContext";

const ADMIN_SECRET = "adminsecret"; // parola secretă pentru admin

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("user");
  const [adminSecret, setAdminSecret] = useState("");
  const [err, setErr] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();
    if (role === "admin" && adminSecret !== ADMIN_SECRET) {
      setErr("Parola secretă de admin este greșită!");
      return;
    }
    const res = await register(username, password, role);
    if (res.success) {
      setErr("");
      setSuccessMessage(res.message);
      // Redirectează la login după 2 secunde
      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } else {
      setErr(res.message || "Eroare la înregistrare!");
      setSuccessMessage("");
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "2rem" }}>
      <h2 style={{ color: "#4f46e5" }}>Register</h2>
      <form className="upload-form" onSubmit={handleRegister} style={{ width: 300 }}>
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
        <select value={role} onChange={e => setRole(e.target.value)}>
          <option value="user">User</option>
          <option value="admin">Admin</option>
        </select>
        {role === "admin" && (
          <input
            type="password"
            placeholder="Parolă secretă admin"
            value={adminSecret}
            onChange={e => setAdminSecret(e.target.value)}
            required
          />
        )}
        <button className="main-btn" type="submit">Register</button>
        {err && <div style={{ color: "red", marginTop: 10 }}>{err}</div>}
        {successMessage && <div style={{ color: "green", marginTop: 10 }}>{successMessage}</div>}
      </form>
      <span>Ai deja cont? <Link to="/login">Login</Link></span>
    </div>
  );
}