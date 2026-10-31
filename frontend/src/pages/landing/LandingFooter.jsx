import { Link } from 'react-router-dom'
import { LeafMark } from '../../assets/illustrations/decor'
import './LandingFooter.css'

export default function LandingFooter() {
  return (
    <footer className="footer">
      <div className="footer__inner">
        <div className="footer__brand">
          <div className="footer__brand-row">
            <LeafMark size={30} />
            <span className="footer__brand-name">NeerNiti</span>
          </div>
          <p className="footer__quote">"Healthy soil builds a better tomorrow."</p>
        </div>

        <nav className="footer__cols" aria-label="Footer">
          <div className="footer__col">
            <h4 className="footer__col-title">Platform</h4>
            <Link to="/app">Dashboard</Link>
            <Link to="/app/analyze">Analyze Soil</Link>
            <Link to="/app/history">History</Link>
          </div>
          <div className="footer__col">
            <h4 className="footer__col-title">Learn</h4>
            <a href="#challenge">The Challenge</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#why-us">Why Us</a>
          </div>
        </nav>
      </div>

      <div className="footer__bar">
        <span>© {new Date().getFullYear()} NeerNiti. All rights reserved.</span>
        <span className="footer__note">
          Recommendations are advisory. Consult a certified agronomist for field-specific decisions.
        </span>
      </div>
    </footer>
  )
}
