import { Link } from 'react-router-dom'
import Button from '../../components/ui/Button'
import LanguageToggle from '../../components/ui/LanguageToggle'
import { LeafMark } from '../../assets/illustrations/decor'
import { useLanguage } from '../../context/language-context'
import './LandingNav.css'

export default function LandingNav() {
  const { t } = useLanguage()

  return (
    <header className="landing-nav">
      <div className="landing-nav__inner">
        <Link to="/" className="landing-nav__brand">
          <LeafMark size={32} />
          <span className="landing-nav__brand-text">
            <span className="landing-nav__brand-name">NeerNiti</span>
            <span className="landing-nav__brand-tag">{t('Smarter Soil. Better Harvests.')}</span>
          </span>
        </Link>

        <nav className="landing-nav__links" aria-label="Primary">
          <a href="#challenge">{t('The Challenge')}</a>
          <a href="#how-it-works">{t('How It Works')}</a>
          <a href="#why-us">{t('Why Us')}</a>
        </nav>

        <LanguageToggle />
        <Button as="link" to="/app" variant="primary" size="md">
          {t('Open Dashboard')}
        </Button>
      </div>
    </header>
  )
}
