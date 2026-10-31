import { useCallback, useMemo, useState } from 'react'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import { Input, Select } from '../../components/ui/Field'
import { SkeletonCard } from '../../components/ui/Feedback'
import { EmptyState, ErrorState } from '../../components/ui/States'
import PageHeader from '../../components/app/PageHeader'
import FarmSwitcher from '../../components/app/FarmSwitcher'
import RecommendationCard from '../../components/app/RecommendationCard'
import { useFarm } from '../../context/farm-context'
import { useAsync } from '../../hooks/useAsync'
import { recommendationsApi } from '../../api/recommendations'
import { LeafSprig, IconArrow } from '../../assets/illustrations/decor'
import './HistoryPage.css'

const STATUS_OPTIONS = [
  { value: 'all', label: 'All statuses' },
  { value: 'feasible', label: 'Plan ready' },
  { value: 'infeasible', label: 'No feasible plan' },
  { value: 'skipped_no_requirements', label: 'Needs crop data' },
  { value: 'skipped_no_prices', label: 'Needs prices' },
]

export default function HistoryPage() {
  const { activeFarmId, activeFarm, hasFarms, loading: farmsLoading } = useFarm()
  const [query, setQuery] = useState('')
  const [status, setStatus] = useState('all')

  const load = useCallback(
    () => (activeFarmId ? recommendationsApi.listForFarm(activeFarmId) : Promise.resolve([])),
    [activeFarmId],
  )
  const { data, loading, error, reload } = useAsync(load, [activeFarmId])

  const filtered = useMemo(() => {
    let list = data || []
    if (status !== 'all') list = list.filter((r) => r.optimization_status === status)
    if (query.trim()) {
      const q = query.trim().toLowerCase()
      list = list.filter((r) => {
        const cls = r.ml_classifier_suggestion?.predicted_class?.toLowerCase() || ''
        return cls.includes(q)
      })
    }
    return list
  }, [data, status, query])

  const header = (
    <PageHeader
      eyebrow="History"
      title="Your recommendation history"
      subtitle={
        activeFarm
          ? `Past soil analyses and recommendations for ${activeFarm.name}.`
          : 'Past soil analyses and fertilizer recommendations.'
      }
      actions={<FarmSwitcher />}
    />
  )

  /* No farms at all */
  if (!farmsLoading && !hasFarms) {
    return (
      <>
        {header}
        <Card tone="surface">
          <EmptyState
            illustration={<LeafSprig className="history-sprig" />}
            title="No farms yet"
            message="Add your first farm and run a soil analysis to start building your history."
            action={
              <Button as="link" to="/app/analyze" variant="primary" iconRight={<IconArrow />}>
                Analyze My Soil
              </Button>
            }
          />
        </Card>
      </>
    )
  }

  return (
    <>
      {header}

      <Card tone="surface" className="history-card">
        {/* Filters */}
        <div className="history-filters">
          <Input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by fertilizer (e.g. Urea)"
            aria-label="Search recommendations"
          />
          <Select value={status} onChange={(e) => setStatus(e.target.value)} aria-label="Filter by status">
            {STATUS_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </Select>
        </div>

        {/* Loading */}
        {loading && (
          <div className="history-list">
            <SkeletonCard lines={2} />
            <SkeletonCard lines={2} />
            <SkeletonCard lines={2} />
          </div>
        )}

        {/* Error */}
        {error && (
          <ErrorState
            title="Couldn't load history"
            message={error.message}
            onRetry={reload}
          />
        )}

        {/* Empty (no recs at all) */}
        {!loading && !error && (data || []).length === 0 && (
          <EmptyState
            illustration={<LeafSprig className="history-sprig" />}
            title="No recommendations yet"
            message="Once you run a soil analysis, your recommendations will appear here for easy reference."
            action={
              <Button as="link" to="/app/analyze" variant="primary" iconRight={<IconArrow />}>
                Run your first analysis
              </Button>
            }
          />
        )}

        {/* Filtered-to-empty */}
        {!loading && !error && (data || []).length > 0 && filtered.length === 0 && (
          <EmptyState
            title="No matches"
            message="No recommendations match your search or filter. Try adjusting them."
          />
        )}

        {/* Results */}
        {!loading && !error && filtered.length > 0 && (
          <>
            <p className="history-count">
              Showing {filtered.length} of {(data || []).length} recommendation
              {(data || []).length === 1 ? '' : 's'}
            </p>
            <div className="history-list">
              {filtered.map((rec) => (
                <RecommendationCard key={rec.id} recommendation={rec} />
              ))}
            </div>
          </>
        )}
      </Card>
    </>
  )
}
