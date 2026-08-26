import { severityTone } from "../lib/format";

export function SeverityGauge({
  value = 0,
  bucket,
}: {
  value?: number;
  bucket?: string;
}) {
  return (
    <div className="severity-widget">
      <div
        className={`gauge ${severityTone(value)}`}
        style={{ "--severity": `${value * 3.6}deg` } as React.CSSProperties}
      >
        <strong>{value}%</strong>
        <span>affected</span>
      </div>
      <div>
        <p className="eyebrow">Severity estimate</p>
        <b className={`gauge-label ${severityTone(value)}`}>
          {bucket ?? "unknown"}
        </b>
      </div>
    </div>
  );
}
