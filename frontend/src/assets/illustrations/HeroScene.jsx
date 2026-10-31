/**
 * HeroScene — original illustrated farmland landscape with a farmer.
 * Semi-realistic flat illustration: layered fields, mountains, trees,
 * sunlight and a farmer surveying the land. Palette matches the design system.
 */
export default function HeroScene({ className }) {
  return (
    <svg
      className={className}
      viewBox="0 0 900 640"
      role="img"
      aria-label="A farmer standing in a lush green crop field with mountains, trees and warm morning sunlight"
      preserveAspectRatio="xMidYMid slice"
    >
      <defs>
        <linearGradient id="hs-sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#d4e6e1" />
          <stop offset="0.55" stopColor="#eae4c9" />
          <stop offset="1" stopColor="#f7f0d4" />
        </linearGradient>
        <radialGradient id="hs-sun" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stopColor="#fdf3cf" />
          <stop offset="0.5" stopColor="#f7e3a6" stopOpacity="0.9" />
          <stop offset="1" stopColor="#f7e3a6" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="hs-field-far" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#9cbd8f" />
          <stop offset="1" stopColor="#7ea86f" />
        </linearGradient>
        <linearGradient id="hs-field-mid" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#6f9661" />
          <stop offset="1" stopColor="#5d8551" />
        </linearGradient>
        <linearGradient id="hs-field-near" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#4e7a42" />
          <stop offset="1" stopColor="#3c6534" />
        </linearGradient>
      </defs>

      {/* Sky */}
      <rect width="900" height="640" fill="url(#hs-sky)" />

      {/* Sun glow */}
      <circle cx="690" cy="150" r="230" fill="url(#hs-sun)" />
      <circle cx="690" cy="150" r="52" fill="#fdf0c4" />

      {/* Distant mountains */}
      <path
        d="M0 250 L120 180 L230 240 L330 160 L470 250 L600 175 L740 250 L900 195 L900 320 L0 320 Z"
        fill="#a7c3b4"
        opacity="0.85"
      />
      <path
        d="M0 285 L150 225 L300 285 L430 215 L560 285 L700 230 L860 290 L900 265 L900 340 L0 340 Z"
        fill="#8fb39f"
        opacity="0.9"
      />

      {/* Tree line */}
      <g opacity="0.95">
        <circle cx="70" cy="300" r="34" fill="#6f9661" />
        <circle cx="110" cy="290" r="30" fill="#7ea86f" />
        <circle cx="150" cy="305" r="28" fill="#6f9661" />
        <circle cx="820" cy="295" r="38" fill="#6f9661" />
        <circle cx="860" cy="300" r="30" fill="#5d8551" />
      </g>

      {/* Far field */}
      <path d="M0 320 L900 320 L900 410 L0 430 Z" fill="url(#hs-field-far)" />
      {/* Small farm houses */}
      <g>
        <rect x="560" y="300" width="34" height="24" rx="2" fill="#e6ddc4" />
        <path d="M556 300 L577 286 L598 300 Z" fill="#b5663f" />
        <rect x="610" y="305" width="28" height="20" rx="2" fill="#efe7d0" />
        <path d="M606 305 L624 293 L642 305 Z" fill="#c07347" />
      </g>

      {/* Mid field with rows */}
      <path d="M0 410 L900 410 L900 500 L0 540 Z" fill="url(#hs-field-mid)" />
      <g stroke="#4e7a42" strokeWidth="2" opacity="0.4">
        <path d="M0 430 L900 418" />
        <path d="M0 455 L900 445" />
        <path d="M0 480 L900 472" />
      </g>

      {/* Near field with crop rows */}
      <path d="M0 500 L900 490 L900 640 L0 640 Z" fill="url(#hs-field-near)" />
      <g stroke="#2f5129" strokeWidth="3" opacity="0.45">
        <path d="M-20 540 L540 510" />
        <path d="M-20 580 L520 530" />
        <path d="M-20 625 L500 560" />
        <path d="M900 520 L620 505" />
        <path d="M900 565 L640 520" />
      </g>
      {/* Crop tufts */}
      <g fill="#6f9661">
        {Array.from({ length: 26 }).map((_, i) => {
          const x = 30 + i * 33
          const y = 560 + (i % 3) * 18
          return (
            <g key={i} transform={`translate(${x} ${y})`}>
              <path d="M0 0 C-4 -14 -2 -22 0 -26 C2 -22 4 -14 0 0 Z" fill="#8fb77f" />
              <path d="M0 -4 C-9 -12 -12 -20 -12 -24 C-6 -22 -2 -14 0 -4 Z" fill="#6f9661" />
              <path d="M0 -4 C9 -12 12 -20 12 -24 C6 -22 2 -14 0 -4 Z" fill="#7ea86f" />
            </g>
          )
        })}
      </g>

      {/* Farmer — surveying the field, seen from behind */}
      <g transform="translate(300 300)">
        {/* legs */}
        <path d="M-22 150 L-18 250 L-2 250 L-4 150 Z" fill="#6c5a3c" />
        <path d="M4 150 L2 250 L18 250 L22 150 Z" fill="#5d4d33" />
        {/* body / kurta */}
        <path
          d="M-40 40 C-46 70 -44 120 -34 158 L34 158 C44 120 46 70 40 40 C30 18 -30 18 -40 40 Z"
          fill="#efe7d2"
        />
        {/* shoulder scarf */}
        <path d="M-40 44 C-10 58 20 58 40 42 L30 76 C8 86 -14 86 -34 76 Z" fill="#c98a3c" opacity="0.9" />
        {/* arm */}
        <path d="M34 54 C50 70 54 110 44 140 L30 136 C38 108 34 76 24 60 Z" fill="#efe7d2" />
        {/* neck + head */}
        <rect x="-10" y="18" width="20" height="18" rx="6" fill="#a8743f" />
        <circle cx="0" cy="2" r="20" fill="#b07c45" />
        {/* turban */}
        <path d="M-22 2 C-22 -22 22 -22 22 2 C22 -6 14 -14 0 -14 C-14 -14 -22 -6 -22 2 Z" fill="#e4ddc8" />
        <path d="M-22 0 C-18 -4 18 -4 22 0 C20 6 -20 6 -22 0 Z" fill="#d6cdb2" />
        {/* tool / staff */}
        <rect x="46" y="60" width="5" height="150" rx="2" fill="#7a5a34" transform="rotate(8 48 130)" />
      </g>

      {/* Foreground leaves (bottom-right accent) */}
      <g transform="translate(790 470)">
        <path d="M0 160 C-30 100 -20 40 20 0 C40 50 40 120 24 160 Z" fill="#4e7a42" />
        <path d="M30 170 C10 110 30 50 70 24 C78 80 70 140 54 174 Z" fill="#6f9661" />
        <path d="M70 180 C60 130 90 80 130 60 C132 112 116 160 100 184 Z" fill="#5d8551" />
      </g>
    </svg>
  )
}
