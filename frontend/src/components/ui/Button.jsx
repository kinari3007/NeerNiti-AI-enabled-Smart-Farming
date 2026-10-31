import { Link } from 'react-router-dom'
import './Button.css'

/**
 * Button — versatile pill button.
 *
 * variant: 'primary' (forest green) | 'gold' | 'ghost' (outlined) | 'ghost-light'
 * size:    'md' | 'lg'
 * as:      render as <a> ('a'), react-router <Link> ('link'), or <button> (default)
 */
export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  as = 'button',
  to,
  href,
  iconLeft,
  iconRight,
  className = '',
  ...props
}) {
  const cls = `btn btn--${variant} btn--${size} ${className}`.trim()

  const content = (
    <>
      {iconLeft && <span className="btn__icon btn__icon--left">{iconLeft}</span>}
      <span className="btn__label">{children}</span>
      {iconRight && <span className="btn__icon btn__icon--right">{iconRight}</span>}
    </>
  )

  if (as === 'link' && to) {
    return (
      <Link to={to} className={cls} {...props}>
        {content}
      </Link>
    )
  }
  if (as === 'a') {
    return (
      <a href={href} className={cls} {...props}>
        {content}
      </a>
    )
  }
  return (
    <button className={cls} {...props}>
      {content}
    </button>
  )
}
