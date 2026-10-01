import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { auth, login } from "../api";

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (auth.access) return <Navigate to="/" replace />;

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(username, password);
      navigate("/");
    } catch (err) {
      setError(err.message === "Failed to fetch" ? "Cannot reach the API server" : err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="login-wrap">
      <form className="card login" onSubmit={submit}>
        <div className="brand big">Quant<span>Power</span> <small>mini</small></div>
        <label>Username<input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus required /></label>
        <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
        <button className="primary" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
        {error && <div className="err">{error}</div>}
      </form>
    </div>
  );
}
