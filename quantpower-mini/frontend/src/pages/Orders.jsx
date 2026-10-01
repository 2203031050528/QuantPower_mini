import { useEffect, useState } from "react";
import { api, asList } from "../api";

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    api("/api/orders/").then((d) => setOrders(asList(d))).catch((e) => setError(e.message)).finally(() => setLoading(false));
  };
  useEffect(load, []);

  return (
    <section className="card">
      <div className="row between">
        <h2>Orders</h2>
        <button className="ghost" onClick={load}>{loading ? "Loading…" : "Refresh"}</button>
      </div>
      {error && <div className="err">{error}</div>}
      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>#</th><th>Time</th><th>Symbol</th><th>Side</th><th>Type</th><th className="r">Qty</th><th className="r">Price</th><th>Mode</th><th>Status</th><th>Broker ID / Error</th></tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td>{o.id}</td>
                <td>{new Date(o.created_at).toLocaleString()}</td>
                <td><strong>{o.symbol}</strong></td>
                <td className={o.side === "BUY" ? "up" : "down"}>{o.side}</td>
                <td>{o.order_type}</td>
                <td className="r">{o.quantity}</td>
                <td className="r">{o.price}</td>
                <td><span className={`pill ${o.mode === "LIVE" ? "offline" : ""}`}>{o.mode}</span></td>
                <td><span className={`status s-${String(o.status).toLowerCase()}`}>{o.status}</span></td>
                <td className="muted small">{o.broker_order_id || o.error_message || "—"}</td>
              </tr>
            ))}
            {!orders.length && !loading && <tr><td colSpan="10" className="muted">No orders yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </section>
  );
}
