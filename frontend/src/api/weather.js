import { http } from './client'

/**
 * Weather + fertilizer catalogue API.
 * Weather:     /api/v1/farms/{farm_id}/weather
 * Fertilizers: /api/v1/fertilizers
 */
export const weatherApi = {
  forFarm: (farmId) => http.get(`/farms/${farmId}/weather`),
}

export const fertilizersApi = {
  list: (page = 1, pageSize = 100) =>
    http.get(`/fertilizers?page=${page}&page_size=${pageSize}`),

  get: (id) => http.get(`/fertilizers/${id}`),

  prices: (productId) =>
    http.get(`/fertilizers/prices${productId ? `?product_id=${productId}` : ''}`),
}
