import { http } from './client'

/**
 * Soil reading API.
 * Backend: /api/v1/farms/{farm_id}/soil-readings and /soil-summary
 */
export const soilApi = {
  listReadings: (farmId) => http.get(`/farms/${farmId}/soil-readings`),

  createReading: (farmId, data) =>
    http.post(`/farms/${farmId}/soil-readings`, data),

  summary: (farmId) => http.get(`/farms/${farmId}/soil-summary`),
}

/* ---- Unit options, straight from the backend schema (soil.py) ---- */
export const EC_UNITS = ['dS/m', 'mS/cm']
export const MOISTURE_UNITS = ['%', 'volumetric']
export const NPK_UNITS = ['mg/kg', 'kg/ha', 'ppm']
export const OC_UNITS = ['%', 'g/kg']
export const DATA_SOURCES = ['manual', 'sensor', 'import']

/* Validation bounds, matching the backend Field constraints */
export const SOIL_BOUNDS = {
  soil_ph: { min: 0, max: 14, agronomicMin: 4, agronomicMax: 8.5 },
  electrical_conductivity: { min: 0, max: 20, highThreshold: 4 },
  soil_moisture: { min: 0, max: 100 },
  nitrogen: { min: 0, max: 10000 },
  phosphorus: { min: 0, max: 10000 },
  potassium: { min: 0, max: 10000 },
  organic_carbon: { min: 0, max: 100 },
}
