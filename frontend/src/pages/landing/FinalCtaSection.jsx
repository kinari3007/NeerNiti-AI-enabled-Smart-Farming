import Button from '../../components/ui/Button'
import { LeafSprig, IconArrow } from '../../assets/illustrations/decor'
import { useLanguage } from '../../context/language-context'
import './FinalCtaSection.css'

export default function FinalCtaSection() {
  const { t } = useLanguage()
  return (
    <section className="final-cta">
      <div className="final-cta__card">
        <div className="final-cta__decor" aria-hidden="true">
          <LeafSprig className="final-cta__sprig" />
        </div>
        <div className="final-cta__content">
          <p className="final-cta__eyebrow">{t('Ready when you are')}</p>
          <h2 className="final-cta__title">
            {t('Technology that understands your land.')}
          </h2>
          <p className="final-cta__lead">
            {t('Start with a single soil analysis and see exactly what your field needs — and what it will cost.')}
          </p>
          <Button as="link" to="/app/analyze" variant="gold" size="lg" iconRight={<IconArrow />}>
            {t('Start Analyzing')}
          </Button>
        </div>
      </div>
    </section>
  )
}
