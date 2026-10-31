/**
 * SoilHealthScene — a cross-section of soil showing a thriving plant,
 * roots and nutrient particles (N, P, K). Used in the soil-health section.
 */
export default function SoilHealthScene({ className }) {
  return (
    <svg
      className={className}
      viewBox="0 0 480 420"
      role="img"
      aria-label="Cross-section of healthy soil showing a plant with deep roots and nutrient particles"
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        <linearGradient id="sh-sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#dcebcf" />
          <stop offset="1" stopColor="#eef0d6" />
        </linearGradient>
        <linearGradient id="sh-soil" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#6a5130" />
          <stop offset="1" stopColor="#402f1b" />
        </linearGradient>
      </defs>

      {/* Sky portion */}
      <rect x="0" y="0" width="480" height="180" rx="24" fill="url(#sh-sky)" />
      {/* Soil portion */}
      <path d="M0 160 L480 160 L480 396 Q480 420 456 420 L24 420 Q0 420 0 396 Z" fill="url(#sh-soil)" />
      <path d="M0 160 L480 160 L480 184 L0 190 Z" fill="#7a5c37" />

      {/* Plant stem + leaves above ground */}
      <path d="M240 168 L240 70" stroke="#4e7a42" strokeWidth="8" strokeLinecap="round" />
      <path d="M240 120 C208 110 186 78 184 46 C220 54 244 90 240 120 Z" fill="#6f9661" />
      <path d="M240 100 C272 90 294 58 296 26 C260 34 236 70 240 100 Z" fill="#7ea86f" />
      <path d="M240 150 C214 144 196 120 196 98 C222 104 242 128 240 150 Z" fill="#8fb77f" />
      <circle cx="240" cy="40" r="12" fill="#d9a441" opacity="0.85" />

      {/* Roots */}
      <g stroke="#caa36a" strokeWidth="4" fill="none" strokeLinecap="round" opacity="0.9">
        <path d="M240 180 C240 220 220 250 198 286" />
        <path d="M240 180 C240 224 262 256 286 294" />
        <path d="M240 200 C228 226 206 240 182 250" />
        <path d="M240 210 C254 234 276 246 300 254" />
        <path d="M212 268 C204 286 196 300 190 320" strokeWidth="3" />
        <path d="M272 276 C280 296 286 310 292 330" strokeWidth="3" />
      </g>

      {/* Nutrient particles */}
      <g fontFamily="var(--font-sans)" fontWeight="700" fontSize="15" textAnchor="middle">
        <circle cx="120" cy="250" r="22" fill="#6f9661" />
        <text x="120" y="256" fill="#fff">N</text>
        <circle cx="360" cy="230" r="22" fill="#d9a441" />
        <text x="360" y="236" fill="#fff">P</text>
        <circle cx="150" cy="340" r="22" fill="#5d8551" />
        <text x="150" y="346" fill="#fff">K</text>
        <circle cx="350" cy="340" r="18" fill="#8a6a3f" />
        <text x="350" y="345" fill="#fff" fontSize="12">pH</text>
      </g>

      {/* Soil specks */}
      <g fill="#5a4428" opacity="0.6">
        <circle cx="70" cy="300" r="3" />
        <circle cx="200" cy="380" r="3" />
        <circle cx="300" cy="300" r="3" />
        <circle cx="420" cy="360" r="3" />
        <circle cx="260" cy="340" r="2.5" />
      </g>
    </svg>
  )
}
