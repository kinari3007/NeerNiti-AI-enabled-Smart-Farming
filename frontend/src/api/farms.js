import { http } from './client'

/**
 * Farm API.
 * Backend: /api/v1/farms
 */
export const farmsApi = {
  list: (page = 1, pageSize = 50) =>
    http.get(`/farms?page=${page}&page_size=${pageSize}`),

  get: (farmId) => http.get(`/farms/${farmId}`),

  create: (data) => http.post('/farms', data),

  update: (farmId, data) => http.patch(`/farms/${farmId}`, data),

  remove: (farmId) => http.del(`/farms/${farmId}`),
}

/** Area unit options accepted by the backend (farm.py pattern). */
export const AREA_UNITS = ['hectare', 'acre', 'sqm', 'bigha']
