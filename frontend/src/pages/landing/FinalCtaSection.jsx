import Button from '../../components/ui/Button'
import { LeafSprig, IconArrow } from '../../assets/illustrations/decor'
import './FinalCtaSection.css'

export default function FinalCtaSection() {
  return (
    <section className="final-cta">
      <div className="final-cta__card">
        <div className="final-cta__decor" aria-hidden="true">
          <LeafSprig className="final-cta__sprig" />
        </div>
        <div className="final-cta__content">
          <p className="final-cta__eyebrow">Ready when you are</p>
          <h2 className="final-cta__title">
            Technology that understands your land.
          </h2>
          <p className="final-cta__lead">
            Start with a single soil analysis and see exactly what your field needs —
            and what it will cost.
          </p>
          <Button as="link" to="/app/analyze" variant="gold" size="lg" iconRight={<IconArrow />}>
            Start Analyzing
          </Button>
        </div>
      </div>
    </section>
  )
}
