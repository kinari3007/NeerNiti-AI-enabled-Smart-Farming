/**
 * FarmerExamineScene — a farmer crouching in a field inspecting crops,
 * with a phone/device in hand. Used in the "Why Choose Us" section.
 */
export default function FarmerExamineScene({ className }) {
  return (
    <svg
      className={className}
      viewBox="0 0 440 360"
      role="img"
      aria-label="A farmer crouching in a green field, examining crops with a handheld device"
      preserveAspectRatio="xMidYMid slice"
    >
      <defs>
        <linearGradient id="fe-sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#d6e7dc" />
          <stop offset="1" stopColor="#ede8cc" />
        </linearGradient>
        <linearGradient id="fe-field" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#6f9661" />
          <stop offset="1" stopColor="#3f6836" />
        </linearGradient>
      </defs>

      <rect width="440" height="360" fill="url(#fe-sky)" />
      <circle cx="360" cy="80" r="46" fill="#f7e3a6" opacity="0.7" />

      {/* Distant hills */}
      <path d="M0 150 L120 110 L240 150 L360 115 L440 150 L440 220 L0 220 Z" fill="#9cbd8f" opacity="0.8" />

      {/* Field */}
      <path d="M0 180 L440 170 L440 360 L0 360 Z" fill="url(#fe-field)" />
      <g stroke="#2f5129" strokeWidth="2.5" opacity="0.4">
        <path d="M-10 230 L450 214" />
        <path d="M-10 270 L450 256" />
        <path d="M-10 315 L450 300" />
      </g>

      {/* Farmer crouching */}
      <g transform="translate(150 150)">
        {/* back leg bent */}
        <path d="M18 96 C40 100 58 116 60 140 L44 150 C40 128 26 116 10 112 Z" fill="#5d4d33" />
        {/* front thigh */}
        <path d="M-6 88 C-28 104 -40 128 -36 150 L-18 150 C-20 128 -6 108 12 98 Z" fill="#6c5a3c" />
        {/* torso leaning forward */}
        <path d="M-18 36 C-30 56 -24 90 2 96 C30 100 44 72 36 44 C28 22 -8 18 -18 36 Z" fill="#e4ddc8" />
        {/* scarf */}
        <path d="M-16 40 C2 52 24 50 36 42 L30 64 C14 72 -6 72 -18 62 Z" fill="#c98a3c" opacity="0.9" />
        {/* arm reaching to crop */}
        <path d="M30 60 C44 72 52 92 48 108 L34 104 C38 90 32 76 20 68 Z" fill="#e4ddc8" />
        <circle cx="52" cy="112" r="8" fill="#b07c45" />
        {/* head */}
        <circle cx="-6" cy="16" r="16" fill="#b07c45" />
        <path d="M-24 14 C-24 -6 12 -6 12 14 C10 6 2 0 -6 0 C-14 0 -22 6 -24 14 Z" fill="#e4ddc8" />
      </g>

      {/* Crop tufts in front */}
      <g>
        {Array.from({ length: 9 }).map((_, i) => {
          const x = 220 + i * 24
          const y = 250 + (i % 2) * 20
          return (
            <g key={i} transform={`translate(${x} ${y})`}>
              <path d="M0 0 C-3 -16 -1 -26 0 -30 C1 -26 3 -16 0 0 Z" fill="#8fb77f" />
              <path d="M0 -4 C-8 -14 -11 -22 -11 -26 C-6 -22 -2 -14 0 -4 Z" fill="#6f9661" />
            </g>
          )
        })}
      </g>
    </svg>
  )
}
