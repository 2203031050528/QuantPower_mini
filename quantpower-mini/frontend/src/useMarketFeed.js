import { useEffect, useRef, useState } from "react";
import { WS_URL } from "./api";

const MAX_POINTS = 120;

// Subscribes to ws/market/ and keeps the latest tick + short history per security_id.
export function useMarketFeed() {
  const [status, setStatus] = useState("connecting");
  const [ticks, setTicks] = useState({});
  const history = useRef({});
  const [, force] = useState(0);

  useEffect(() => {
    let ws;
    let timer;
    let closed = false;

    const connect = () => {
      setStatus("connecting");
      ws = new WebSocket(`${WS_URL}/ws/market/`);
      ws.onopen = () => setStatus("live");
      ws.onclose = () => {
        setStatus("offline");
        if (!closed) timer = setTimeout(connect, 3000);
      };
      ws.onerror = () => ws.close();
      ws.onmessage = (e) => {
        let msg;
        try { msg = JSON.parse(e.data); } catch { return; }
        if (!msg.security_id || msg.ltp == null) return;
        const id = msg.security_id;
        const h = (history.current[id] ||= []);
        h.push(Number(msg.ltp));
        if (h.length > MAX_POINTS) h.shift();
        setTicks((prev) => ({
          ...prev,
          [id]: { ...msg, prev: prev[id]?.ltp ?? msg.ltp, open: prev[id]?.open ?? msg.ltp },
        }));
        force((n) => n + 1);
      };
    };

    connect();
    return () => {
      closed = true;
      clearTimeout(timer);
      ws?.close();
    };
  }, []);

  return { status, ticks, history: history.current };
}
