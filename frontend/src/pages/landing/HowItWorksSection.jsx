import Card from '../../components/ui/Card'
import SectionHeading from '../../components/ui/SectionHeading'
import StepItem from '../../components/ui/StepItem'
import { IconData } from '../../assets/illustrations/decor'
import './HowItWorksSection.css'

const STEPS = [
  {
    title: 'Enter your soil and crop details',
    description:
      'Provide information about your soil, crop, growth stage, and farming conditions. Partial data is fine — we work with what you have.',
  },
  {
    title: 'Our AI analyzes the data',
    description:
      'We use a machine-learning model trained on real agricultural data, combined with agronomic nutrient references.',
  },
  {
    title: 'Get a personalized recommendation',
    description:
      'Receive a cost-optimized fertilizer plan tailored to your specific soil and crop requirements.',
  },
  {
    title: 'Improve your yields',
    description:
      'Make informed decisions, reduce waste, and grow healthier, more productive crops season after season.',
  },
]

export default function HowItWorksSection() {
  return (
    <section className="how" id="how-it-works">
      <div className="how__inner">
        <Card tone="cream" className="how__card">
          <SectionHeading
            eyebrow="How It Works"
            eyebrowIcon={<IconData size={18} />}
            title="From soil sample to smart decision in four steps."
          />
          <ol className="how__steps">
            {STEPS.map((step, i) => (
              <StepItem
                key={i}
                number={i + 1}
                title={step.title}
                description={step.description}
                last={i === STEPS.length - 1}
              />
            ))}
          </ol>
        </Card>
      </div>
    </section>
  )
}
