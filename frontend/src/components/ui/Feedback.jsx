import './Feedback.css'

/** Inline spinner. */
export function Spinner({ size = 20, className = '' }) {
  return (
    <span
      className={`spinner ${className}`.trim()}
      style={{ width: size, height: size }}
      role="status"
      aria-label="Loading"
    />
  )
}

/** Rectangular skeleton placeholder. */
export function Skeleton({ width = '100%', height = 16, radius = 8, className = '' }) {
  return (
    <span
      className={`skeleton ${className}`.trim()}
      style={{ width, height, borderRadius: radius }}
      aria-hidden="true"
    />
  )
}

/** A card-shaped skeleton block for list/grid loading states. */
export function SkeletonCard({ lines = 3 }) {
  return (
    <div className="skeleton-card" aria-hidden="true">
      <Skeleton width="40%" height={20} />
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton key={i} width={i === lines - 1 ? '60%' : '100%'} height={12} />
      ))}
    </div>
  )
}

/** Status badge. tone: success | warning | neutral | gold | info */
export function Badge({ tone = 'neutral', children, className = '' }) {
  return <span className={`badge badge--${tone} ${className}`.trim()}>{children}</span>
}
