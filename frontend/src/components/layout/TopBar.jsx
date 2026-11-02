import { IconBell, IconMenu } from '../../assets/illustrations/decor'
import LanguageToggle from '../ui/LanguageToggle'
import { useLanguage } from '../../context/language-context'
import './TopBar.css'

function greeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Good Morning'
  if (h < 17) return 'Good Afternoon'
  return 'Good Evening'
}

export default function TopBar({ onMenu, name = 'Farmer', subtitle }) {
  const { t } = useLanguage()
  const displayName = name === 'Farmer' ? t('Farmer') : name
  return (
    <header className="topbar">
      <button className="topbar__menu" onClick={onMenu} aria-label={t('Open menu')}>
        <IconMenu size={24} />
      </button>

      <div className="topbar__greeting">
        <p className="topbar__hello">
          {t(greeting())}
          {displayName ? `, ${displayName}!` : '!'}
        </p>
        {subtitle && <p className="topbar__sub">{subtitle}</p>}
      </div>

      <div className="topbar__actions">
        <LanguageToggle />
        <button className="topbar__icon-btn" aria-label={t('Notifications')}>
          <IconBell size={20} />
        </button>
        <div className="topbar__profile">
          <span className="topbar__avatar" aria-hidden="true">
            {displayName ? displayName.charAt(0).toUpperCase() : 'F'}
          </span>
          <span className="topbar__profile-text">
            <span className="topbar__profile-name">{displayName}</span>
            <span className="topbar__profile-role">{t('Farmer')}</span>
          </span>
        </div>
      </div>
    </header>
  )
}
