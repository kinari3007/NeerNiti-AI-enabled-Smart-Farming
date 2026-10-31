import SectionHeading from '../../components/ui/SectionHeading'
import Card from '../../components/ui/Card'
import StatPill from '../../components/ui/StatPill'
import OrganicImage from '../../components/ui/OrganicImage'
import FarmerExamineScene from '../../assets/illustrations/FarmerExamineScene'
import { IconLeafCheck, IconCoin, IconSprout, IconData } from '../../assets/illustrations/decor'
import './WhyUsSection.css'

const CAPABILITIES = [
  {
    icon: <IconData size={22} />,
    title: 'Data-driven soil analysis',
    text: 'Aggregates multiple soil readings per farm with proper statistics and flags out-of-range values.',
  },
  {
    icon: <IconCoin size={22} />,
    title: 'Cost-optimized recommendations',
    text: 'A linear-programming solver finds the lowest-cost fertilizer mix that meets your crop nutrient targets.',
  },
  {
    icon: <IconLeafCheck size={22} />,
    title: 'Honest and transparent',
    text: 'Every recommendation shows its assumptions, price sources, and any unmet requirements — no black boxes.',
  },
]

export default function WhyUsSection() {
  return (
    <section className="why" id="why-us">
      <div className="why__inner">
        <SectionHeading
          eyebrow="Why Choose Us"
          eyebrowIcon={<IconSprout size={18} />}
          title="Better decisions, healthier crops."
          lead="Neer Niti analyzes your soil nutrients, crop needs, and environmental conditions to recommend the right fertilizer — because every field is unique."
          align="center"
        />

        <div className="why__grid">
          <div className="why__art">
            <OrganicImage shape="blob-2" className="why__blob">
              <FarmerExamineScene />
            </OrganicImage>
          </div>

          <div className="why__cards">
            {CAPABILITIES.map((c, i) => (
              <Card key={i} tone="surface" className="why__capability">
                <span className="why__cap-icon" aria-hidden="true">
                  {c.icon}
                </span>
                <div>
                  <h3 className="why__cap-title">{c.title}</h3>
                  <p className="why__cap-text">{c.text}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>

        <div className="why__stats">
          <StatPill icon={<IconSprout size={22} />} label="Higher Productivity" />
          <StatPill icon={<IconLeafCheck size={22} />} label="Healthier Soil" />
          <StatPill icon={<IconCoin size={22} />} label="Lower Costs" />
          <StatPill icon={<IconData size={22} />} label="Sustainable Farming" />
        </div>
      </div>
    </section>
  )
}
