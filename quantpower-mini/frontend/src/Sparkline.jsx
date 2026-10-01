export default function Sparkline({ data = [], height = 160 }) {
  if (data.length < 2) return <div className="spark-empty" style={{ height }}>Waiting for ticks…</div>;
  const w = 600;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const pts = data.map((v, i) => [
    (i / (data.length - 1)) * w,
    height - 8 - ((v - min) / range) * (height - 16),
  ]);
  const line = pts.map((p) => p.join(",")).join(" ");
  const up = data[data.length - 1] >= data[0];
  const color = up ? "var(--up)" : "var(--down)";
  return (
    <svg viewBox={`0 0 ${w} ${height}`} preserveAspectRatio="none" className="spark" style={{ height }}>
      <polygon points={`0,${height} ${line} ${w},${height}`} fill={color} opacity="0.12" />
      <polyline points={line} fill="none" stroke={color} strokeWidth="2" vectorEffect="non-scaling-stroke" />
    </svg>
  );
}
