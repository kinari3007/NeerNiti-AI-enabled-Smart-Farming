import './Field.css'

/**
 * Field — label + control wrapper with helper text and error.
 * Wrap any input/select. Use the Input and Select helpers below for consistency.
 */
export function Field({ label, htmlFor, hint, error, required, children, className = '' }) {
  return (
    <div className={`field ${error ? 'field--error' : ''} ${className}`.trim()}>
      {label && (
        <label className="field__label" htmlFor={htmlFor}>
          {label}
          {required && <span className="field__req" aria-hidden="true"> *</span>}
        </label>
      )}
      {children}
      {hint && !error && <p className="field__hint">{hint}</p>}
      {error && (
        <p className="field__error" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}

export function Input({ className = '', suffix, ...props }) {
  if (suffix) {
    return (
      <div className="input-wrap">
        <input className={`input ${className}`.trim()} {...props} />
        <span className="input-wrap__suffix">{suffix}</span>
      </div>
    )
  }
  return <input className={`input ${className}`.trim()} {...props} />
}

export function Select({ className = '', children, ...props }) {
  return (
    <div className="select-wrap">
      <select className={`select ${className}`.trim()} {...props}>
        {children}
      </select>
      <span className="select-wrap__chevron" aria-hidden="true">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <path d="M6 9l6 6 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </span>
    </div>
  )
}

export function Textarea({ className = '', ...props }) {
  return <textarea className={`textarea ${className}`.trim()} {...props} />
}
