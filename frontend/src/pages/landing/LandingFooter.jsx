import { Link } from 'react-router-dom'
import { LeafMark } from '../../assets/illustrations/decor'
import { useLanguage } from '../../context/language-context'
import './LandingFooter.css'

export default function LandingFooter() {
  const { t } = useLanguage()
  return (
    <footer className="footer">
      <div className="footer__inner">
        <div className="footer__brand">
          <div className="footer__brand-row">
            <LeafMark size={30} />
            <span className="footer__brand-name">NeerNiti</span>
          </div>
          <p className="footer__quote">"{t('Healthy soil builds a better tomorrow.')}"</p>
        </div>

        <nav className="footer__cols" aria-label="Footer">
          <div className="footer__col">
            <h4 className="footer__col-title">{t('Platform')}</h4>
            <Link to="/app">{t('Dashboard')}</Link>
            <Link to="/app/analyze">{t('Analyze Soil')}</Link>
            <Link to="/app/history">{t('History')}</Link>
          </div>
          <div className="footer__col">
            <h4 className="footer__col-title">{t('Learn')}</h4>
            <a href="#challenge">{t('The Challenge')}</a>
            <a href="#how-it-works">{t('How It Works')}</a>
            <a href="#why-us">{t('Why Us')}</a>
          </div>
        </nav>
      </div>

      <div className="footer__bar">
        <span>© {new Date().getFullYear()} NeerNiti. {t('All rights reserved.')}</span>
        <span className="footer__note">
          {t('Recommendations are advisory. Consult a certified agronomist for field-specific decisions.')}
        </span>
      </div>
    </footer>
  )
}
