import './Stepper.css'

/**
 * Stepper — horizontal progress indicator for the multi-step form.
 * steps: [{ label }]; current: 0-based index of the active step.
 */
export default function Stepper({ steps, current }) {
  return (
    <ol className="stepper" aria-label="Progress">
      {steps.map((step, i) => {
        const state = i < current ? 'done' : i === current ? 'active' : 'upcoming'
        return (
          <li key={i} className={`stepper__item stepper__item--${state}`}>
            <span className="stepper__marker" aria-hidden="true">
              {state === 'done' ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M5 12.5l4 4 10-10" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              ) : (
                i + 1
              )}
            </span>
            <span className="stepper__label">{step.label}</span>
            {i < steps.length - 1 && <span className="stepper__bar" aria-hidden="true" />}
          </li>
        )
      })}
    </ol>
  )
}
