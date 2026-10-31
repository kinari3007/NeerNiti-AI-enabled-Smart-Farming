import { useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import { Badge, Skeleton } from '../../components/ui/Feedback'
import { ErrorState } from '../../components/ui/States'
import { useAsync } from '../../hooks/useAsync'
import { recommendationsApi, OPTIMIZATION_STATUS } from '../../api/recommendations'
import { formatDateTime, formatMoney, formatNumber, formatPercent } from '../../utils/format'
import { LeafMark, IconArrow, IconLeafCheck, IconSprout } from '../../assets/illustrations/decor'
import './RecommendationPage.css'

export default function RecommendationPage() {
  const { id } = useParams()
  const load = useCallback(() => recommendationsApi.get(id), [id])
  const { data: rec, loading, error, reload } = useAsync(load, [id])

  if (loading) {
    return (
      <div className="rec-page">
        <Skeleton width={160} height={16} />
        <Skeleton width="100%" height={220} radius={24} />
        <Skeleton width="100%" height={160} radius={24} />
      </div>
    )
  }

  if (error) {
    return (
      <div className="rec-page">
        <ErrorState
          title="Couldn't load this recommendation"
          message={error.message}
          onRetry={reload}
        />
        <div className="rec-page__back">
          <Button as="link" to="/app/history" variant="ghost">
            Back to history
          </Button>
        </div>
      </div>
    )
  }

  const ml = rec.ml_classifier_suggestion
  const statusInfo = OPTIMIZATION_STATUS[rec.optimization_status] || {
    label: rec.optimization_status,
    tone: 'neutral',
    note: '',
  }
  const probability = ml ? formatPercent(ml.confidence) : null
  const plan = rec.recommended_fertilizers || []
  const balance = rec.nutrient_balance

  return (
    <div className="rec-page">
      <div className="rec-page__top">
        <Link to="/app/history" className="rec-page__backlink">
          ← History
        </Link>
        <span className="rec-page__date">{formatDateTime(rec.created_at)}</span>
      </div>

      {/* ---- Hero: the ML-suggested fertilizer ---- */}
      <Card tone="plain" className="rec-hero">
        <div className="rec-hero__body">
          <span className="rec-hero__eyebrow">
            <IconSprout size={18} /> Suggested fertilizer category
          </span>
          {ml ? (
            <>
              <h1 className="rec-hero__fertilizer">{ml.predicted_class}</h1>
              {probability && (
                <p className="rec-hero__prob">
                  Model probability for this class: <strong>{probability}</strong>
                </p>
              )}
            </>
          ) : (
            <>
              <h1 className="rec-hero__fertilizer rec-hero__fertilizer--muted">
                Not available
              </h1>
              <p className="rec-hero__prob">
                The ML category suggestion could not be produced for this request.
              </p>
            </>
          )}
        </div>
        <div className="rec-hero__art" aria-hidden="true">
          <LeafMark size={64} />
        </div>
      </Card>

      {/* Honest disclaimer about what the ML output means */}
      {ml?.disclaimer && <p className="rec-disclaimer">{ml.disclaimer}</p>}

      {/* ---- Top classes (real softmax probabilities) ---- */}
      {ml?.top_classes?.length > 0 && (
        <Card tone="surface" className="rec-section">
          <h2 className="rec-section__title">Model's top candidates</h2>
          <p className="rec-section__note">
            These are the classifier's raw probabilities — a statistical signal, not a
            calibrated certainty.
          </p>
          <ul className="rec-topclasses">
            {ml.top_classes.map((tc) => {
              const pct = Math.round((tc.probability || 0) * 100)
              return (
                <li key={tc.class} className="rec-topclass">
                  <span className="rec-topclass__name">{tc.class}</span>
                  <span className="rec-topclass__bar" aria-hidden="true">
                    <span className="rec-topclass__fill" style={{ width: `${pct}%` }} />
                  </span>
                  <span className="rec-topclass__pct">{pct}%</span>
                </li>
              )
            })}
          </ul>
        </Card>
      )}

      {/* ---- Optimization status ---- */}
      <Card tone="surface" className="rec-section">
        <div className="rec-section__head">
          <h2 className="rec-section__title">Cost-optimized plan</h2>
          <Badge tone={statusInfo.tone}>{statusInfo.label}</Badge>
        </div>
        <p className="rec-section__note">{statusInfo.note}</p>

        {rec.optimization_status === 'feasible' && plan.length > 0 ? (
          <>
            {rec.estimated_total_cost != null && (
              <div className="rec-cost">
                <span className="rec-cost__label">Estimated total cost</span>
                <span className="rec-cost__value">
                  {formatMoney(rec.estimated_total_cost, rec.cost_currency || 'INR')}
                </span>
              </div>
            )}
            <div className="rec-plan">
              {plan.map((item) => (
                <div key={item.product_id} className="rec-plan__item">
                  <div className="rec-plan__head">
                    <span className="rec-plan__name">{item.product_name}</span>
                    {!item.price_verified && (
                      <Badge tone="gold">
                        {item.price_source === 'illustrative_sample'
                          ? 'Illustrative price'
                          : 'Unverified price'}
                      </Badge>
                    )}
                  </div>
                  <div className="rec-plan__stats">
                    <div>
                      <span className="rec-plan__stat-label">Quantity</span>
                      <span className="rec-plan__stat-value">
                        {formatNumber(item.quantity_kg_total, 1)} kg
                        <span className="rec-plan__stat-sub">
                          {' '}({formatNumber(item.quantity_kg_per_ha, 1)} kg/ha)
                        </span>
                      </span>
                    </div>
                    <div>
                      <span className="rec-plan__stat-label">Unit price</span>
                      <span className="rec-plan__stat-value">
                        {formatMoney(item.price_per_kg, item.currency)}/kg
                      </span>
                    </div>
                    <div>
                      <span className="rec-plan__stat-label">Line cost</span>
                      <span className="rec-plan__stat-value">
                        {formatMoney(item.cost_total, item.currency)}
                      </span>
                    </div>
                  </div>
                  <p className="rec-plan__provenance">
                    Price source: {item.price_source}
                    {item.price_recorded_at
                      ? ` · recorded ${formatDateTime(item.price_recorded_at)}`
                      : ''}
                  </p>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="rec-plan-empty">
            <IconLeafCheck size={28} />
            <p>
              No fertilizer plan was produced for this recommendation. See the notes
              below for why, and what to adjust.
            </p>
          </div>
        )}
      </Card>

      {/* ---- Nutrient requirements & balance ---- */}
      {(rec.nutrient_requirements || balance) && (
        <Card tone="surface" className="rec-section">
          <h2 className="rec-section__title">Nutrient requirements</h2>
          {rec.nutrient_requirement_source && (
            <p className="rec-section__note">{rec.nutrient_requirement_source}</p>
          )}

          <div className="rec-nutrients">
            {['N', 'P', 'K'].map((key) => {
              const req = rec.nutrient_requirements?.[key]
              const supplied = balance
                ? balance[`${key.toLowerCase()}_supplied_kg_per_ha`]
                : null
              const deficit = balance
                ? balance[`${key.toLowerCase()}_deficit_kg_per_ha`]
                : null
              const label =
                key === 'N' ? 'Nitrogen (N)' : key === 'P' ? 'Phosphorus (P₂O₅)' : 'Potassium (K₂O)'
              return (
                <div key={key} className="rec-nutrient">
                  <span className="rec-nutrient__label">{label}</span>
                  <div className="rec-nutrient__rows">
                    {req != null && (
                      <span className="rec-nutrient__row">
                        Required <strong>{formatNumber(req, 1)} kg/ha</strong>
                      </span>
                    )}
                    {supplied != null && (
                      <span className="rec-nutrient__row">
                        Supplied <strong>{formatNumber(supplied, 1)} kg/ha</strong>
                      </span>
                    )}
                    {deficit != null && deficit > 0.01 && (
                      <span className="rec-nutrient__row rec-nutrient__row--deficit">
                        Short by {formatNumber(deficit, 1)} kg/ha
                      </span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
          {balance?.unit_convention && (
            <p className="rec-section__fine">{balance.unit_convention}</p>
          )}
        </Card>
      )}

      {/* ---- Warnings & assumptions ---- */}
      {(rec.warnings?.length > 0 || rec.assumptions?.length > 0) && (
        <div className="rec-notes-grid">
          {rec.warnings?.length > 0 && (
            <Card tone="surface" className="rec-section">
              <h2 className="rec-section__title">Warnings</h2>
              <ul className="rec-notes rec-notes--warn">
                {rec.warnings.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </Card>
          )}
          {rec.assumptions?.length > 0 && (
            <Card tone="surface" className="rec-section">
              <h2 className="rec-section__title">Assumptions</h2>
              <ul className="rec-notes">
                {rec.assumptions.map((a, i) => (
                  <li key={i}>{a}</li>
                ))}
              </ul>
            </Card>
          )}
        </div>
      )}

      <div className="rec-page__actions">
        <Button as="link" to="/app/analyze" variant="primary" iconRight={<IconArrow />}>
          Run another analysis
        </Button>
        <Button as="link" to="/app/history" variant="ghost">
          View all recommendations
        </Button>
      </div>
    </div>
  )
}
