import SectionHeading from '../../components/ui/SectionHeading'
import SoilHealthScene from '../../assets/illustrations/SoilHealthScene'
import { IconSprout } from '../../assets/illustrations/decor'
import { useLanguage } from '../../context/language-context'
import './SoilHealthSection.css'

const NUTRIENTS = [
  { label: 'Nitrogen (N)', role: 'Drives leafy, vegetative growth and vivid green color.' },
  { label: 'Phosphorus (P₂O₅)', role: 'Builds strong roots and supports flowering and fruiting.' },
  { label: 'Potassium (K₂O)', role: 'Improves resilience, water regulation, and crop quality.' },
]

export default function SoilHealthSection() {
  const { t } = useLanguage()
  return (
    <section className="soil">
      <div className="soil__inner">
        <div className="soil__art">
          <SoilHealthScene className="soil__scene" />
        </div>

        <div className="soil__text">
          <SectionHeading
            eyebrow={t('Soil & Nutrients')}
            eyebrowIcon={<IconSprout size={18} />}
            title={t('Understanding what your soil truly needs.')}
            lead={t("Balanced nutrition is the difference between a surviving crop and a thriving one. We account for the three core nutrients and your soil's pH together.")}
          />
          <ul className="soil__nutrients">
            {NUTRIENTS.map((n, i) => (
              <li key={i} className="soil__nutrient">
                <span className="soil__nutrient-dot" aria-hidden="true" />
                <div>
                  <strong className="soil__nutrient-label">{t(n.label)}</strong>
                  <p className="soil__nutrient-role">{t(n.role)}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
