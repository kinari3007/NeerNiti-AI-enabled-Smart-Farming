import './StepItem.css'

/**
 * StepItem — numbered process step with title + description.
 * Used in the "How It Works" panel.
 */
export default function StepItem({ number, title, description, last = false }) {
  return (
    <li className={`step-item ${last ? 'step-item--last' : ''}`.trim()}>
      <div className="step-item__marker" aria-hidden="true">
        <span className="step-item__number">{number}</span>
      </div>
      <div className="step-item__body">
        <h3 className="step-item__title">{title}</h3>
        <p className="step-item__desc">{description}</p>
      </div>
    </li>
  )
}
