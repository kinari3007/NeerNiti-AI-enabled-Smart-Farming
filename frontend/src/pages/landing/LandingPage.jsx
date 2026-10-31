import LandingNav from './LandingNav'
import HeroSection from './HeroSection'
import ChallengeSection from './ChallengeSection'
import HowItWorksSection from './HowItWorksSection'
import WhyUsSection from './WhyUsSection'
import SoilHealthSection from './SoilHealthSection'
import FinalCtaSection from './FinalCtaSection'
import LandingFooter from './LandingFooter'

export default function LandingPage() {
  return (
    <>
      <LandingNav />
      <main>
        <HeroSection />
        <ChallengeSection />
        <HowItWorksSection />
        <WhyUsSection />
        <SoilHealthSection />
        <FinalCtaSection />
      </main>
      <LandingFooter />
    </>
  )
}
