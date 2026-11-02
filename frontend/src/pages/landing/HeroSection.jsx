import Button from '../../components/ui/Button'
import HeroScene from '../../assets/illustrations/HeroScene'
import { IconArrow, IconPlay } from '../../assets/illustrations/decor'
import { useLanguage } from '../../context/language-context'
import './HeroSection.css'

export default function HeroSection() {
  const { t } = useLanguage()
  return (
    <section className="hero">
      <div className="hero__art" aria-hidden="false">
        <HeroScene className="hero__scene" />
        <div className="hero__overlay" />
      </div>

      <div className="hero__content">
        <h1 className="hero__title">
          {t('Grow Better.')}
          <br />
          {t('Farm Smarter.')}
        </h1>
        <p className="hero__lead">
          {t('AI-powered soil analysis and personalized fertilizer recommendations for healthier crops, lower costs, and higher yields — because every field is unique.')}
        </p>
        <div className="hero__actions">
          <Button as="link" to="/app/analyze" variant="primary" size="lg" iconRight={<IconArrow />}>
            {t('Analyze My Soil')}
          </Button>
          <Button as="a" href="#how-it-works" variant="ghost-light" size="lg" iconLeft={<IconPlay />}>
            {t('Learn How It Works')}
          </Button>
        </div>
      </div>
    </section>
  )
}
