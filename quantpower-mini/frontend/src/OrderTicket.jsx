import { useEffect, useState } from "react";
import { api } from "./api";

export default function OrderTicket({ instrument, ltp, onPlaced }) {
  const [form, setForm] = useState({ side: "BUY", quantity: 1, order_type: "MARKET", price: "", mode: "VIRTUAL" });
  const [msg, setMsg] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => setMsg(null), [instrument?.security_id]);

  if (!instrument) return <div className="card muted">Select an instrument to trade.</div>;

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    if (form.mode === "LIVE" && !confirm("Place a LIVE order with your broker?")) return;
    setBusy(true);
    setMsg(null);
    try {
      const res = await api("/api/orders/create/", {
        method: "POST",
        body: {
          security_id: instrument.security_id,
          symbol: instrument.symbol,
          side: form.side,
          quantity: Number(form.quantity),
          order_type: form.order_type,
          price: form.order_type === "LIMIT" ? Number(form.price) : ltp ?? 0,
          mode: form.mode,
        },
      });
      setMsg({ ok: true, text: `Order #${res.order_id} → ${res.status}` });
      onPlaced?.();
    } catch (err) {
      setMsg({ ok: false, text: err.message });
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="card ticket" onSubmit={submit}>
      <h3>Order · {instrument.symbol}</h3>
      <div className="seg">
        {["BUY", "SELL"].map((s) => (
          <button type="button" key={s} className={`${s.toLowerCase()} ${form.side === s ? "on" : ""}`}
            onClick={() => setForm({ ...form, side: s })}>{s}</button>
        ))}
      </div>
      <label>Quantity<input type="number" min="1" value={form.quantity} onChange={set("quantity")} required /></label>
      <label>Type
        <select value={form.order_type} onChange={set("order_type")}>
          <option>MARKET</option><option>LIMIT</option>
        </select>
      </label>
      {form.order_type === "LIMIT" && (
        <label>Limit price<input type="number" step="0.05" value={form.price} onChange={set("price")} required /></label>
      )}
      <label>Mode
        <select value={form.mode} onChange={set("mode")}>
          <option value="VIRTUAL">VIRTUAL (paper)</option>
          <option value="LIVE">LIVE (broker)</option>
        </select>
      </label>
      <button className={`primary ${form.side.toLowerCase()}`} disabled={busy}>
        {busy ? "Placing…" : `${form.side} ${form.quantity} @ ${form.order_type === "LIMIT" ? form.price || "—" : "MKT"}`}
      </button>
      {msg && <div className={msg.ok ? "ok" : "err"}>{msg.text}</div>}
    </form>
  );
}
