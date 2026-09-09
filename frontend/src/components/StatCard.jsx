import {
  ArrowDownRight,
  ArrowUpRight,
} from "lucide-react";
import "./styles/StatCard.css";

function StatCard({
  title,
  value,
  change,
  changeType = "neutral",
  subtitle,
  icon,
  accent = "default",
  detail,
}) {
  const positive = changeType === "positive";
  const negative = changeType === "negative";

  return (
    <article className={`premium-stat-card ${accent}`}>
      <div className="stat-accent-line"></div>

      <div className="premium-stat-top">
        <span className="premium-stat-title">
          {title}
        </span>

        <div className="premium-stat-icon">
          {icon}
        </div>
      </div>

      <div className="premium-stat-value">
        {value}
      </div>

      <div className="premium-stat-footer">
        {change && (
          <span
            className={`premium-change ${
              positive
                ? "up"
                : negative
                ? "down"
                : ""
            }`}
          >
            {positive && (
              <ArrowUpRight size={13} />
            )}

            {negative && (
              <ArrowDownRight size={13} />
            )}

            {change}
          </span>
        )}

        <span>{subtitle}</span>
      </div>

      {detail && (
        <div className="stat-detail">
          {detail}
        </div>
      )}
    </article>
  );
}

export default StatCard;