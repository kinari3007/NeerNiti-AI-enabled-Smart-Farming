/**
 * Decorative + functional line icons and small illustrations.
 * Consistent stroke style; inherit currentColor so they adapt to context.
 */

export function LeafMark({ className, size = 28 }) {
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 32 32"
      role="img"
      aria-label="Neer Niti leaf mark"
    >
      <path
        d="M27 5c0 13-8 21-19 22 0-3 1-6 3-9 3-4 8-6 8-6-5 1-9 3-12 7-1-9 6-15 20-14Z"
        fill="#6f9661"
      />
      <path d="M8 27C13 19 20 13 25 10" stroke="#234d35" strokeWidth="1.6" fill="none" strokeLinecap="round" />
    </svg>
  )
}

export function LeafSprig({ className }) {
  return (
    <svg
      className={className}
      viewBox="0 0 120 220"
      role="img"
      aria-label="A delicate leaf sprig"
      preserveAspectRatio="xMidYMax meet"
    >
      <path d="M60 220 L60 30" stroke="#8fb77f" strokeWidth="3" strokeLinecap="round" />
      <g fill="#6f9661">
        <path d="M60 60 C40 54 28 38 26 20 C48 24 62 42 60 60 Z" />
        <path d="M60 50 C80 44 92 28 94 10 C72 14 58 32 60 50 Z" />
        <path d="M60 110 C42 104 30 88 28 70 C50 74 62 92 60 110 Z" />
        <path d="M60 100 C78 94 90 78 92 60 C72 64 58 82 60 100 Z" />
        <path d="M60 160 C44 154 34 140 32 124 C52 128 62 144 60 160 Z" />
        <path d="M60 150 C76 144 86 130 88 114 C70 118 58 134 60 150 Z" />
      </g>
    </svg>
  )
}

/* ---- functional icons (sidebar / features) ---- */
const base = {
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.8,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
}

export function IconHome({ size = 22 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path {...base} d="M4 11.5 12 4l8 7.5" />
      <path {...base} d="M5.5 10.5V20h13v-9.5" />
      <path {...base} d="M10 20v-5h4v5" />
    </svg>
  )
}

export function IconSoil({ size = 22 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path {...base} d="M12 13c0-4 2-7 6-8-1 4-3 7-6 8Z" />
      <path {...base} d="M12 13c0-3-1.5-5.5-5-6.5C7.5 10 9.5 12 12 13Z" />
      <path {...base} d="M12 13v5" />
      <path {...base} d="M4 20h16" />
    </svg>
  )
}

export function IconHistory({ size = 22 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path {...base} d="M3.5 12a8.5 8.5 0 1 0 2.6-6.1" />
      <path {...base} d="M5.5 3.5v3h3" />
      <path {...base} d="M12 8v4l3 2" />
    </svg>
  )
}

export function IconProfile({ size = 22 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <circle {...base} cx="12" cy="8.5" r="3.5" />
      <path {...base} d="M5 19c1-3.5 4-5 7-5s6 1.5 7 5" />
    </svg>
  )
}

export function IconArrow({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path {...base} d="M5 12h14" />
      <path {...base} d="M13 6l6 6-6 6" />
    </svg>
  )
}

export function IconPlay({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <circle {...base} cx="12" cy="12" r="9" />
      <path d="M10 8.5v7l6-3.5-6-3.5Z" fill="currentColor" />
    </svg>
  )
}

export function IconSprout({ size = 24 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path {...base} d="M12 20v-7" />
      <path {...base} d="M12 13c0-3 2-5 5-5.5C16.5 11 14.5 13 12 13Z" />
      <path {...base} d="M12 14c0-2.5-1.5-4.5-4.5-5C8 12 10 14 12 14Z" />
    </svg>
  )
}

export function IconData({ size = 24 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <ellipse {...base} cx="12" cy="6" rx="7" ry="3" />
      <path {...base} d="M5 6v12c0 1.7 3.1 3 7 3s7-1.3 7-3V6" />
      <path {...base} d="M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3" />
    </svg>
  )
}

export function IconCoin({ size = 24 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <circle {...base} cx="12" cy="12" r="8" />
      <path {...base} d="M12 7.5v9M9.5 9.5c0-1.2 1.1-2 2.5-2s2.5.6 2.5 1.8c0 2.4-5 1.4-5 3.9 0 1.2 1.1 1.8 2.5 1.8s2.5-.8 2.5-2" />
    </svg>
  )
}

export function IconLeafCheck({ size = 24 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path {...base} d="M20 4c0 9-6 14-13 15 0-2 .8-4 2-6 2-2.7 5.5-4 5.5-4" />
      <path {...base} d="M8.5 13.5l2 2 4-4.5" />
    </svg>
  )
}

export function IconBell({ size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path {...base} d="M6 9a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6Z" />
      <path {...base} d="M10 19a2 2 0 0 0 4 0" />
    </svg>
  )
}

export function IconMenu({ size = 24 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path {...base} d="M4 7h16M4 12h16M4 17h16" />
    </svg>
  )
}

export function IconClose({ size = 24 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path {...base} d="M6 6l12 12M18 6 6 18" />
    </svg>
  )
}
