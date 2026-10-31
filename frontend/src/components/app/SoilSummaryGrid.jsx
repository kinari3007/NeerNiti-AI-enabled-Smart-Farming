import { formatNumber } from '../../utils/format'
import './SoilSummaryGrid.css'

const PARAM_LABELS = {
  ph: 'Soil pH',
  ec: 'Electrical Conductivity',
  moisture: 'Moisture',
  nitrogen: 'Nitrogen (N)',
  phosphorus: 'Phosphorus (P)',
  potassium: 'Potassium (K)',
  organic_carbon: 'Organic Carbon',
}

const ORDER = ['ph', 'nitrogen', 'phosphorus', 'potassium', 'ec', 'moisture', 'organic_carbon']

/**
 * SoilSummaryGrid — renders only the parameters the backend actually
 * aggregated. Each stat is real (mean across readings). No invented scores.
 */
export default function SoilSummaryGrid({ summary }) {
  if (!summary) return null

  const present = ORDER.filter((key) => summary[key])

  if (!present.length) {
    return (
      <p className="soil-grid__empty">
        No numeric soil measurements have been recorded yet. Add a soil reading to see
        aggregated statistics.
      </p>
    )
  }

  return (
    <div className="soil-grid">
      {present.map((key) => {
        const stat = summary[key]
        return (
          <div key={key} className="soil-grid__item">
            <span className="soil-grid__label">{PARAM_LABELS[key]}</span>
            <span className="soil-grid__value">
              {formatNumber(stat.mean, 2)}
              {stat.unit && <span className="soil-grid__unit"> {stat.unit}</span>}
            </span>
            <span className="soil-grid__range">
              {stat.count === 1
                ? 'from 1 reading'
                : `avg of ${stat.count} readings · ${formatNumber(stat.min, 1)}–${formatNumber(stat.max, 1)}`}
            </span>
          </div>
        )
      })}
    </div>
  )
}
