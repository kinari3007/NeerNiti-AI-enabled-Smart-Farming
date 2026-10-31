import { http } from './client'

/**
 * Recommendation API.
 * Backend: /api/v1/farms/{farm_id}/recommendations and
 *          /api/v1/recommendations/{recommendation_id}
 */
export const recommendationsApi = {
  create: (farmId, data) =>
    http.post(`/farms/${farmId}/recommendations`, data),

  listForFarm: (farmId) => http.get(`/farms/${farmId}/recommendations`),

  get: (recommendationId) => http.get(`/recommendations/${recommendationId}`),
}

/** Human-readable labels for the backend optimization_status values. */
export const OPTIMIZATION_STATUS = {
  feasible: {
    label: 'Plan ready',
    tone: 'success',
    note: 'A cost-optimized fertilizer plan was found.',
  },
  infeasible: {
    label: 'No feasible plan',
    tone: 'warning',
    note: 'No available fertilizer combination could meet the nutrient targets.',
  },
  skipped_no_requirements: {
    label: 'Needs crop data',
    tone: 'neutral',
    note: 'This crop/stage is not in the nutrient reference table, so optimization was skipped.',
  },
  skipped_no_prices: {
    label: 'Needs prices',
    tone: 'neutral',
    note: 'No usable fertilizer prices were available for optimization.',
  },
  pending: { label: 'Pending', tone: 'neutral', note: 'Not yet computed.' },
  error: { label: 'Error', tone: 'warning', note: 'An error occurred during optimization.' },
}
