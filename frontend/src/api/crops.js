import { http } from './client'

/**
 * Crop API.
 * Backend: /api/v1/crops and /api/v1/farms/{farm_id}/crop-selections
 */
export const cropsApi = {
  list: () => http.get('/crops'),

  get: (cropId) => http.get(`/crops/${cropId}`),

  listSelections: (farmId) => http.get(`/farms/${farmId}/crop-selections`),

  createSelection: (farmId, data) =>
    http.post(`/farms/${farmId}/crop-selections`, data),
}

/** Growth stages accepted by the backend (crop.py VALID_GROWTH_STAGES). */
export const GROWTH_STAGES = [
  'Sowing',
  'Germination',
  'Vegetative',
  'Flowering',
  'Maturity',
  'Harvest',
]

/** Safely parse the JSON-encoded typical_growth_stages field. */
export function parseGrowthStages(raw) {
  if (!raw) return GROWTH_STAGES
  try {
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) && parsed.length ? parsed : GROWTH_STAGES
  } catch {
    return GROWTH_STAGES
  }
}
