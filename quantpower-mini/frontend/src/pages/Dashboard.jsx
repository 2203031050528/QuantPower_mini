import { useEffect, useMemo, useState } from "react";
import { api, asList } from "../api";
import { useMarketFeed } from "../useMarketFeed";
import Sparkline from "../Sparkline";
import OrderTicket from "../OrderTicket";

const fmt = (n) => (n == null ? "—" : Number(n).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 }));

export default function Dashboard() {
  const { status, ticks, history } = useMarketFeed();
  const [instruments, setInstruments] = useState([]);
  const [selected, setSelected] = useState(null);
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api("/api/market/instruments/").then((d) => setInstruments(asList(d))).catch((e) => setError(e.message));
  }, []);

  // Instruments from the DB plus any security streaming on the feed but not in the DB (e.g. mock_market)
  const rows = useMemo(() => {
    const map = new Map(instruments.map((i) => [String(i.security_id), i]));
    Object.values(ticks).forEach((t) => {
      if (!map.has(t.security_id)) map.set(t.security_id, { security_id: t.security_id, symbol: t.symbol || t.security_id, exchange: t.exchange_segment || "" });
    });
    const q = query.trim().toLowerCase();
    return [...map.values()]
      .filter((i) => !q || i.symbol.toLowerCase().includes(q) || String(i.security_id).includes(q))
      .sort((a, b) => (ticks[b.security_id] ? 1 : 0) - (ticks[a.security_id] ? 1 : 0));
  }, [instruments, ticks, query]);

  const current = selected || rows[0];
  const tick = current && ticks[current.security_id];
  const change = tick ? tick.ltp - tick.open : 0;

  return (
    <div className="grid-dash">
      <section className="card watchlist">
        <div className="row between">
          <h3>Watchlist</h3>
          <span className={`pill ${status}`}>{status}</span>
        </div>
        <input placeholder="Search symbol / id" value={query} onChange={(e) => setQuery(e.target.value)} />
        {error && <div className="err">{error}</div>}
        <ul>
          {rows.map((i) => {
            const t = ticks[i.security_id];
            const dir = t ? (t.ltp >= t.prev ? "up" : "down") : "";
            return (
              <li key={i.security_id} className={current?.security_id === i.security_id ? "active" : ""} onClick={() => setSelected(i)}>
                <div>
                  <strong>{i.symbol}</strong>
                  <small>{i.exchange || i.segment} · {i.security_id}</small>
                </div>
                <span className={`num ${dir}`}>{t ? fmt(t.ltp) : "—"}</span>
              </li>
            );
          })}
          {!rows.length && <li className="muted">No instruments. Start <code>mock_market</code> or add instruments.</li>}
        </ul>
      </section>

      <section className="card chart">
        {current ? (
          <>
            <div className="row between">
              <div>
                <h2>{current.symbol}</h2>
                <small className="muted">{current.exchange || current.segment} · {current.security_id}</small>
              </div>
              <div className="right">
                <div className="ltp">{fmt(tick?.ltp)}</div>
                <div className={`num ${change >= 0 ? "up" : "down"}`}>
                  {tick ? `${change >= 0 ? "+" : ""}${fmt(change)} (session)` : "no ticks yet"}
                </div>
              </div>
            </div>
            <Sparkline data={history[current.security_id] || []} height={240} />
            <small className="muted">Last update: {tick?.timestamp || "—"}</small>
          </>
        ) : (
          <div className="muted">Waiting for market data…</div>
        )}
      </section>

      <OrderTicket instrument={current} ltp={tick?.ltp} />
    </div>
  );
}
