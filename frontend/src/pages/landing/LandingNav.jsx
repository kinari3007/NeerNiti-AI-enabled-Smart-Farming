import { Link } from 'react-router-dom'
import Button from '../../components/ui/Button'
import { LeafMark } from '../../assets/illustrations/decor'
import './LandingNav.css'

export default function LandingNav() {
  return (
    <header className="landing-nav">
      <div className="landing-nav__inner">
        <Link to="/" className="landing-nav__brand">
          <LeafMark size={32} />
          <span className="landing-nav__brand-text">
            <span className="landing-nav__brand-name">NeerNiti</span>
            <span className="landing-nav__brand-tag">Smarter Soil. Better Harvests.</span>
          </span>
        </Link>

        <nav className="landing-nav__links" aria-label="Primary">
          <a href="#challenge">The Challenge</a>
          <a href="#how-it-works">How It Works</a>
          <a href="#why-us">Why Us</a>
        </nav>

        <Button as="link" to="/app" variant="primary" size="md">
          Open Dashboard
        </Button>
      </div>
    </header>
  )
}
