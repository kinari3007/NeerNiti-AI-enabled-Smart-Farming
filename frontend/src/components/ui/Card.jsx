import './Card.css'

/**
 * Card — rounded surface with soft shadow.
 * tone: 'surface' (white) | 'cream' | 'sage' | 'forest' (dark) | 'plain'
 */
export default function Card({
  children,
  tone = 'surface',
  className = '',
  as: Tag = 'div',
  ...props
}) {
  return (
    <Tag className={`card card--${tone} ${className}`.trim()} {...props}>
      {children}
    </Tag>
  )
}
