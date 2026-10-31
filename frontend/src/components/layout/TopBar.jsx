import { IconBell, IconMenu } from '../../assets/illustrations/decor'
import './TopBar.css'

function greeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Good Morning'
  if (h < 17) return 'Good Afternoon'
  return 'Good Evening'
}

export default function TopBar({ onMenu, name = 'Farmer', subtitle }) {
  return (
    <header className="topbar">
      <button className="topbar__menu" onClick={onMenu} aria-label="Open menu">
        <IconMenu size={24} />
      </button>

      <div className="topbar__greeting">
        <p className="topbar__hello">
          {greeting()}
          {name ? `, ${name}!` : '!'}
        </p>
        {subtitle && <p className="topbar__sub">{subtitle}</p>}
      </div>

      <div className="topbar__actions">
        <button className="topbar__icon-btn" aria-label="Notifications">
          <IconBell size={20} />
        </button>
        <div className="topbar__profile">
          <span className="topbar__avatar" aria-hidden="true">
            {name ? name.charAt(0).toUpperCase() : 'F'}
          </span>
          <span className="topbar__profile-text">
            <span className="topbar__profile-name">{name}</span>
            <span className="topbar__profile-role">Farmer</span>
          </span>
        </div>
      </div>
    </header>
  )
}
