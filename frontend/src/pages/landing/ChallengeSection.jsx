import SectionHeading from '../../components/ui/SectionHeading'
import Button from '../../components/ui/Button'
import OrganicImage from '../../components/ui/OrganicImage'
import PlantingScene from '../../assets/illustrations/PlantingScene'
import { IconArrow, IconSprout } from '../../assets/illustrations/decor'
import './ChallengeSection.css'

export default function ChallengeSection() {
  return (
    <section className="challenge" id="challenge">
      <div className="challenge__text">
        <SectionHeading
          eyebrow="The Challenge"
          eyebrowIcon={<IconSprout size={18} />}
          title="Healthy soil is the foundation of every good harvest."
        />
        <p className="challenge__body">
          Many farmers struggle to determine the right fertilizer for their soil and
          crops. The wrong choice leads to reduced yields, higher costs, and long-term
          soil degradation. Guesswork is expensive — and the land pays the price.
        </p>
        <p className="challenge__body">
          Neer Niti replaces guesswork with data. We analyze your soil nutrients, crop
          needs, and local conditions to recommend precisely what your field requires —
          no more, no less.
        </p>
        <Button as="link" to="/app/analyze" variant="ghost" iconRight={<IconArrow />}>
          Learn More
        </Button>
      </div>

      <div className="challenge__art">
        <OrganicImage shape="blob-1" className="challenge__blob">
          <PlantingScene />
        </OrganicImage>
      </div>
    </section>
  )
}
