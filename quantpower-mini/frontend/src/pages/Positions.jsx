import { useEffect, useState } from "react";
import { api, asList } from "../api";
import { useMarketFeed } from "../useMarketFeed";

const fmt = (n) => Number(n).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export default function Positions() {
  const { ticks } = useMarketFeed();
  const [positions, setPositions] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/api/orders/positions/").then((d) => setPositions(asList(d))).catch((e) => setError(e.message));
  }, []);

  let totalUnreal = 0;
  let totalReal = 0;

  const rows = positions.map((p) => {
    const ltp = ticks[p.security_id]?.ltp;
    const unreal = ltp != null ? (ltp - Number(p.average_price)) * p.quantity : null;
    if (unreal != null) totalUnreal += unreal;
    totalReal += Number(p.realized_pnl);
    return { ...p, ltp, unreal };
  });

  return (
    <>
      <div className="stats">
        <div className="card stat"><small>Open positions</small><b>{positions.filter((p) => p.quantity).length}</b></div>
        <div className="card stat"><small>Unrealized P&amp;L</small><b className={totalUnreal >= 0 ? "up" : "down"}>{fmt(totalUnreal)}</b></div>
        <div className="card stat"><small>Realized P&amp;L</small><b className={totalReal >= 0 ? "up" : "down"}>{fmt(totalReal)}</b></div>
      </div>
      <section className="card">
        <h2>Positions</h2>
        {error && <div className="err">{error}</div>}
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Symbol</th><th className="r">Qty</th><th className="r">Avg price</th><th className="r">LTP</th><th className="r">Unrealized</th><th className="r">Realized</th><th>Updated</th></tr>
            </thead>
            <tbody>
              {rows.map((p) => (
                <tr key={p.id}>
                  <td><strong>{p.symbol}</strong> <small className="muted">{p.security_id}</small></td>
                  <td className="r">{p.quantity}</td>
                  <td className="r">{fmt(p.average_price)}</td>
                  <td className="r">{p.ltp != null ? fmt(p.ltp) : "—"}</td>
                  <td className={`r ${p.unreal >= 0 ? "up" : "down"}`}>{p.unreal != null ? fmt(p.unreal) : "—"}</td>
                  <td className={`r ${p.realized_pnl >= 0 ? "up" : "down"}`}>{fmt(p.realized_pnl)}</td>
                  <td className="muted small">{new Date(p.updated_at).toLocaleString()}</td>
                </tr>
              ))}
              {!rows.length && <tr><td colSpan="7" className="muted">No positions.</td></tr>}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}
