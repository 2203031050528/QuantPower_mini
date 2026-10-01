import { useEffect, useState } from "react";
import { api } from "../api";

export default function Broker() {
  const [account, setAccount] = useState(null);
  const [form, setForm] = useState({ client_id: "", access_token: "" });
  const [proxy, setProxy] = useState(null);
  const [msg, setMsg] = useState(null);
  const [preview, setPreview] = useState(null);
  const [pv, setPv] = useState({ security_id: "", quantity: 1, side: "BUY", order_type: "MARKET" });

  useEffect(() => {
    api("/api/dhan/account/")
      .then((a) => { setAccount(a); setForm({ client_id: a.client_id, access_token: "" }); })
      .catch(() => setAccount(false));
    api("/api/proxy/status/").then(setProxy).catch((e) => setProxy({ active: false, error: e.message }));
  }, []);

  const save = async (e) => {
    e.preventDefault();
    try {
      const a = await api("/api/dhan/account/", { method: "POST", body: form });
      setAccount(a);
      setForm({ ...form, access_token: "" });
      setMsg({ ok: true, text: "Dhan account saved" });
    } catch (err) {
      setMsg({ ok: false, text: err.message });
    }
  };

  const runPreview = async (e) => {
    e.preventDefault();
    try {
      setPreview(await api("/api/orders/dhan/preview/", { method: "POST", body: { ...pv, quantity: Number(pv.quantity) } }));
    } catch (err) {
      setPreview({ error: err.message });
    }
  };

  return (
    <div className="grid-2">
      <form className="card" onSubmit={save}>
        <div className="row between">
          <h2>Dhan account</h2>
          <span className={`pill ${account?.is_active ? "live" : "offline"}`}>{account ? (account.is_active ? "connected" : "inactive") : "not connected"}</span>
        </div>
        <label>Client ID<input value={form.client_id} onChange={(e) => setForm({ ...form, client_id: e.target.value })} required /></label>
        <label>Access token<input type="password" placeholder={account ? "re-enter token to update" : ""} value={form.access_token} onChange={(e) => setForm({ ...form, access_token: e.target.value })} required /></label>
        <button className="primary">Save</button>
        {msg && <div className={msg.ok ? "ok" : "err"}>{msg.text}</div>}
      </form>

      <section className="card">
        <div className="row between">
          <h2>Egress proxy</h2>
          <span className={`pill ${proxy?.active ? "live" : "offline"}`}>{proxy ? (proxy.active ? "allocated" : "none") : "…"}</span>
        </div>
        {proxy?.active ? (
          <dl className="kv">
            {Object.entries(proxy.proxy || {}).map(([k, v]) => (<div key={k}><dt>{k}</dt><dd>{String(v)}</dd></div>))}
          </dl>
        ) : (
          <p className="muted">{proxy?.error || "Loading…"}</p>
        )}
      </section>

      <form className="card span-2" onSubmit={runPreview}>
        <h2>Dhan order preview <small className="muted">(dry run — nothing is sent)</small></h2>
        <div className="row wrap">
          <label>Security ID<input value={pv.security_id} onChange={(e) => setPv({ ...pv, security_id: e.target.value })} required /></label>
          <label>Qty<input type="number" min="1" value={pv.quantity} onChange={(e) => setPv({ ...pv, quantity: e.target.value })} /></label>
          <label>Side<select value={pv.side} onChange={(e) => setPv({ ...pv, side: e.target.value })}><option>BUY</option><option>SELL</option></select></label>
          <label>Type<select value={pv.order_type} onChange={(e) => setPv({ ...pv, order_type: e.target.value })}><option>MARKET</option><option>LIMIT</option></select></label>
          <button className="primary">Preview</button>
        </div>
        {preview && <pre className={preview.error ? "err" : ""}>{preview.error || JSON.stringify(preview, null, 2)}</pre>}
      </form>
    </div>
  );
}
