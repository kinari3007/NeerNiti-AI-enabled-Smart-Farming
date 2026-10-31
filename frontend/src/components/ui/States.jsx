import Button from './Button'
import { LeafMark } from '../../assets/illustrations/decor'
import './States.css'

/** Empty state with an agricultural illustration and optional action. */
export function EmptyState({ illustration, title, message, action }) {
  return (
    <div className="state state--empty">
      <div className="state__art" aria-hidden="true">
        {illustration || <LeafMark size={44} />}
      </div>
      <h3 className="state__title">{title}</h3>
      {message && <p className="state__message">{message}</p>}
      {action && <div className="state__action">{action}</div>}
    </div>
  )
}

/** Error state with retry. */
export function ErrorState({ title = 'Something went wrong', message, onRetry }) {
  return (
    <div className="state state--error">
      <div className="state__art state__art--error" aria-hidden="true">
        <svg width="44" height="44" viewBox="0 0 24 24" fill="none">
          <path
            d="M12 3 2.5 20h19L12 3Z"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinejoin="round"
          />
          <path d="M12 10v4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
          <circle cx="12" cy="17" r="0.9" fill="currentColor" />
        </svg>
      </div>
      <h3 className="state__title">{title}</h3>
      {message && <p className="state__message">{message}</p>}
      {onRetry && (
        <div className="state__action">
          <Button variant="ghost" onClick={onRetry}>
            Try again
          </Button>
        </div>
      )}
    </div>
  )
}
