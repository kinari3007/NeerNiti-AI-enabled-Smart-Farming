import './OrganicImage.css'

/**
 * OrganicImage — wraps an illustration in a soft organic blob shape.
 * shape: 'blob-1' | 'blob-2' | 'rounded'
 */
export default function OrganicImage({ children, shape = 'blob-1', className = '' }) {
  return (
    <div className={`organic-image organic-image--${shape} ${className}`.trim()}>
      {children}
    </div>
  )
}
