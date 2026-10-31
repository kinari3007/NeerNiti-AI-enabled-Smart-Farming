import { useCallback } from 'react'
import { Link } from 'react-router-dom'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import { SkeletonCard, Skeleton } from '../../components/ui/Feedback'
import { EmptyState, ErrorState } from '../../components/ui/States'
import FarmSwitcher from '../../components/app/FarmSwitcher'
import RecommendationCard from '../../components/app/RecommendationCard'
import SoilSummaryGrid from '../../components/app/SoilSummaryGrid'
import { useFarm } from '../../context/farm-context'
import { useAsync } from '../../hooks/useAsync'
import { session } from '../../api/session'
import { soilApi } from '../../api/soil'
import { recommendationsApi } from '../../api/recommendations'
import FarmerExamineScene from '../../assets/illustrations/FarmerExamineScene'
import { LeafMark, IconArrow, IconSoil, IconHistory, IconProfile } from '../../assets/illustrations/decor'
import './DashboardPage.css'

export default function DashboardPage() {
  const { activeFarmId, activeFarm, hasFarms, loading: farmsLoading, error: farmsError, reloadFarms } =
    useFarm()
  const name = session.getName()

  const loadSummary = useCallback(
    () => (activeFarmId ? soilApi.summary(activeFarmId) : Promise.resolve(null)),
    [activeFarmId],
  )
  const loadRecs = useCallback(
    () => (activeFarmId ? recommendationsApi.listForFarm(activeFarmId) : Promise.resolve([])),
    [activeFarmId],
  )

  const summary = useAsync(loadSummary, [activeFarmId])
  const recs = useAsync(loadRecs, [activeFarmId])

  /* ---- Banner (always shown) ---- */
  const banner = (
    <Card tone="plain" className="dash-banner">
      <div className="dash-banner__content">
        <span className="dash-banner__eyebrow">
          {name ? `Welcome back, ${name}` : 'Welcome to NeerNiti'}
        </span>
        <h1 className="dash-banner__title">Let's make your field more productive.</h1>
        <p className="dash-banner__lead">
          Record your soil readings and get a cost-optimized fertilizer recommendation
          tailored to your crop.
        </p>
        <div className="dash-banner__actions">
          <Button as="link" to="/app/analyze" variant="gold" size="lg" iconRight={<IconArrow />}>
            Analyze My Soil
          </Button>
        </div>
      </div>
      <div className="dash-banner__art" aria-hidden="true">
        <FarmerExamineScene />
      </div>
    </Card>
  )

  /* ---- No farms yet ---- */
  if (!farmsLoading && !hasFarms && !farmsError) {
    return (
      <>
        {banner}
        <Card tone="surface" className="dash-section">
          <EmptyState
            illustration={<LeafMark size={44} />}
            title="Start by adding your farm"
            message="Create your first farm to record soil readings and generate recommendations. It only takes a moment."
            action={
              <Button as="link" to="/app/analyze" variant="primary" iconRight={<IconArrow />}>
                Add a farm & analyze
              </Button>
            }
          />
        </Card>
      </>
    )
  }

  return (
    <>
      {banner}

      {/* Active farm bar */}
      <div className="dash-farmbar">
        <div>
          <span className="dash-farmbar__label">Active farm</span>
          <span className="dash-farmbar__name">
            {farmsLoading ? <Skeleton width={160} height={20} /> : activeFarm?.name || '—'}
          </span>
        </div>
        <FarmSwitcher />
      </div>

      <div className="dash-grid">
        {/* Soil overview */}
        <Card tone="surface" className="dash-section dash-section--soil">
          <div className="dash-section__head">
            <h2 className="dash-section__title">Soil & nutrient overview</h2>
            <Button as="link" to="/app/analyze" variant="ghost" size="md">
              Add reading
            </Button>
          </div>

          {summary.loading && <Skeleton width="100%" height={120} radius={14} />}
          {summary.error && (
            <ErrorState
              title="Couldn't load soil data"
              message={summary.error.message}
              onRetry={summary.reload}
            />
          )}
          {!summary.loading && !summary.error && (
            <>
              <SoilSummaryGrid summary={summary.data} />
              {summary.data?.warnings?.length > 0 && (
                <ul className="dash-notes">
                  {summary.data.warnings.map((w, i) => (
                    <li key={i}>{w}</li>
                  ))}
                </ul>
              )}
            </>
          )}
        </Card>

        {/* Quick navigation */}
        <Card tone="sage" className="dash-section dash-quicknav">
          <h2 className="dash-section__title">Quick actions</h2>
          <div className="dash-quicknav__list">
            <Link to="/app/analyze" className="dash-quicknav__item">
              <IconSoil />
              <span>Analyze Soil</span>
            </Link>
            <Link to="/app/history" className="dash-quicknav__item">
              <IconHistory />
              <span>View History</span>
            </Link>
            <Link to="/app/profile" className="dash-quicknav__item">
              <IconProfile />
              <span>Farm Profile</span>
            </Link>
          </div>
        </Card>
      </div>

      {/* Recent recommendations */}
      <Card tone="surface" className="dash-section">
        <div className="dash-section__head">
          <h2 className="dash-section__title">Recent recommendations</h2>
          {recs.data?.length > 0 && (
            <Button as="link" to="/app/history" variant="ghost" size="md" iconRight={<IconArrow />}>
              View all
            </Button>
          )}
        </div>

        {recs.loading && (
          <div className="dash-rec-list">
            <SkeletonCard lines={2} />
            <SkeletonCard lines={2} />
          </div>
        )}

        {recs.error && (
          <ErrorState
            title="Couldn't load recommendations"
            message={recs.error.message}
            onRetry={recs.reload}
          />
        )}

        {!recs.loading && !recs.error && recs.data?.length === 0 && (
          <EmptyState
            illustration={<LeafMark size={40} />}
            title="No recommendations yet"
            message="Run your first soil analysis to see personalized fertilizer recommendations here."
            action={
              <Button as="link" to="/app/analyze" variant="primary" iconRight={<IconArrow />}>
                Analyze My Soil
              </Button>
            }
          />
        )}

        {!recs.loading && !recs.error && recs.data?.length > 0 && (
          <div className="dash-rec-list">
            {recs.data.slice(0, 4).map((rec) => (
              <RecommendationCard key={rec.id} recommendation={rec} />
            ))}
          </div>
        )}
      </Card>

      {farmsError && (
        <Card tone="surface" className="dash-section">
          <ErrorState
            title="Couldn't load your farms"
            message={farmsError.message}
            onRetry={reloadFarms}
          />
        </Card>
      )}
    </>
  )
}
