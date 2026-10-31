import { Link } from 'react-router-dom'
import { Badge } from '../ui/Feedback'
import { OPTIMIZATION_STATUS } from '../../api/recommendations'
import { formatDateTime, formatMoney } from '../../utils/format'
import { IconArrow, IconSprout } from '../../assets/illustrations/decor'
import './RecommendationCard.css'

/**
 * RecommendationCard — compact summary of one recommendation.
 * Shows only real backend data: ML-suggested category, status, cost, date.
 */
export default function RecommendationCard({ recommendation }) {
  const rec = recommendation
  const statusInfo = OPTIMIZATION_STATUS[rec.optimization_status] || {
    label: rec.optimization_status,
    tone: 'neutral',
  }
  const suggested = rec.ml_classifier_suggestion?.predicted_class

  return (
    <Link to={`/app/recommendations/${rec.id}`} className="rec-card">
      <div className="rec-card__top">
        <span className="rec-card__icon" aria-hidden="true">
          <IconSprout size={22} />
        </span>
        <div className="rec-card__headline">
          <span className="rec-card__suggested">
            {suggested ? suggested : 'Recommendation'}
          </span>
          <span className="rec-card__date">{formatDateTime(rec.created_at)}</span>
        </div>
        <span className="rec-card__arrow" aria-hidden="true">
          <IconArrow size={18} />
        </span>
      </div>

      <div className="rec-card__meta">
        <Badge tone={statusInfo.tone}>{statusInfo.label}</Badge>
        {rec.estimated_total_cost != null && (
          <span className="rec-card__cost">
            {formatMoney(rec.estimated_total_cost, rec.cost_currency || 'INR')}
            <span className="rec-card__cost-label"> est. total</span>
          </span>
        )}
      </div>
    </Link>
  )
}
