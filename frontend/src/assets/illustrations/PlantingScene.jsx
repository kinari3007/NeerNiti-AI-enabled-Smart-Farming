/**
 * PlantingScene — hands cradling a young seedling in rich soil.
 * Used in the "Challenge" section inside an organic blob mask.
 */
export default function PlantingScene({ className }) {
  return (
    <svg
      className={className}
      viewBox="0 0 520 440"
      role="img"
      aria-label="Two hands gently cradling a young green seedling growing in dark, rich soil"
      preserveAspectRatio="xMidYMid slice"
    >
      <defs>
        <linearGradient id="ps-bg" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#e8e8c9" />
          <stop offset="1" stopColor="#cdd8b4" />
        </linearGradient>
        <radialGradient id="ps-light" cx="0.5" cy="0.3" r="0.7">
          <stop offset="0" stopColor="#fdf6da" stopOpacity="0.9" />
          <stop offset="1" stopColor="#fdf6da" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="ps-soil" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#5a4428" />
          <stop offset="1" stopColor="#3b2d1a" />
        </linearGradient>
        <linearGradient id="ps-skin" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#c08a52" />
          <stop offset="1" stopColor="#a8743f" />
        </linearGradient>
      </defs>

      <rect width="520" height="440" fill="url(#ps-bg)" />
      <ellipse cx="260" cy="130" rx="260" ry="180" fill="url(#ps-light)" />

      {/* Cupped hands */}
      <path
        d="M70 300 C60 250 110 230 150 250 C180 236 230 236 260 250 C290 236 340 236 370 250 C410 230 460 250 450 300 C440 360 360 410 260 410 C160 410 80 360 70 300 Z"
        fill="url(#ps-skin)"
      />
      <path
        d="M110 300 C140 350 200 376 260 376 C320 376 380 350 410 300 C388 300 320 316 260 316 C200 316 132 300 110 300 Z"
        fill="#9a6938"
        opacity="0.5"
      />
      {/* Fingers hint */}
      <g fill="#b07c45" opacity="0.8">
        <path d="M150 252 C158 234 150 214 138 206 C130 224 136 244 150 252 Z" />
        <path d="M370 252 C362 234 370 214 382 206 C390 224 384 244 370 252 Z" />
      </g>

      {/* Mound of soil */}
      <path d="M170 300 C180 262 340 262 350 300 C330 326 190 326 170 300 Z" fill="url(#ps-soil)" />
      {/* Soil specks */}
      <g fill="#6b5231">
        <circle cx="210" cy="296" r="4" />
        <circle cx="250" cy="304" r="3" />
        <circle cx="296" cy="292" r="4" />
        <circle cx="322" cy="300" r="3" />
        <circle cx="236" cy="288" r="2.5" />
      </g>

      {/* Seedling */}
      <path d="M260 290 L260 206" stroke="#4e7a42" strokeWidth="6" strokeLinecap="round" />
      <path d="M260 230 C236 222 220 196 218 172 C244 178 262 204 260 230 Z" fill="#6f9661" />
      <path d="M260 214 C284 206 300 180 302 156 C276 162 258 188 260 214 Z" fill="#7ea86f" />
      <path d="M260 196 C250 180 252 158 262 144 C272 158 272 182 260 196 Z" fill="#8fb77f" />
    </svg>
  )
}
