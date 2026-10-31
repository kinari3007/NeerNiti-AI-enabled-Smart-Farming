import './StatPill.css'

/**
 * StatPill — small icon + label feature marker.
 * Used in the "Better Decisions" strip (Higher Productivity, Healthier Soil, etc.)
 */
export default function StatPill({ icon, label }) {
  return (
    <div className="stat-pill">
      <span className="stat-pill__icon" aria-hidden="true">
        {icon}
      </span>
      <span className="stat-pill__label">{label}</span>
    </div>
  )
}
