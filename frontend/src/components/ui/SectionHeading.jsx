import './SectionHeading.css'

/**
 * SectionHeading — eyebrow label + serif title, optional lead paragraph.
 * tone: 'dark' (default) | 'light' for use on dark backgrounds
 * align: 'left' (default) | 'center'
 */
export default function SectionHeading({
  eyebrow,
  eyebrowIcon,
  title,
  lead,
  tone = 'dark',
  align = 'left',
  className = '',
}) {
  return (
    <div className={`section-heading section-heading--${tone} section-heading--${align} ${className}`.trim()}>
      {eyebrow && (
        <span className="section-heading__eyebrow">
          {eyebrowIcon && <span className="section-heading__eyebrow-icon">{eyebrowIcon}</span>}
          {eyebrow}
        </span>
      )}
      {title && <h2 className="section-heading__title">{title}</h2>}
      {lead && <p className="section-heading__lead">{lead}</p>}
    </div>
  )
}
