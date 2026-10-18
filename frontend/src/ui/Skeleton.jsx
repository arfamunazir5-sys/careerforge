import "../theme.css";
import "./States.css";
import Card from "./Card";

export default function Skeleton({ width = "100%", height = 14, radius = 6 }) {
  return (
    <div
      className="st-skel"
      style={{ width, height, borderRadius: radius }}
      aria-hidden="true"
    />
  );
}

export function SkeletonCard({ lines = 3, title = true }) {
  return (
    <Card>
      <div className="st-skel-lines" role="status" aria-label="Loading">
        {title && <Skeleton width="40%" height={18} />}
        {Array.from({ length: lines }).map((_, i) => (
          <Skeleton key={i} width={i === lines - 1 ? "70%" : "100%"} />
        ))}
      </div>
    </Card>
  );
}