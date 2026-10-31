/**
 * Lightweight local session helpers.
 *
 * The backend does not implement user authentication yet, so the frontend
 * tracks the farmer's display name and the currently-active farm locally.
 * This is NOT a security boundary — it is a convenience for a single-device
 * demo/local workflow. When real auth is added, replace this module.
 */

const NAME_KEY = 'neerniti.farmer_name'
const FARM_KEY = 'neerniti.active_farm_id'

export const session = {
  getName() {
    return localStorage.getItem(NAME_KEY) || ''
  },
  setName(name) {
    if (name) localStorage.setItem(NAME_KEY, name)
    else localStorage.removeItem(NAME_KEY)
  },
  getActiveFarmId() {
    return localStorage.getItem(FARM_KEY) || ''
  },
  setActiveFarmId(id) {
    if (id) localStorage.setItem(FARM_KEY, id)
    else localStorage.removeItem(FARM_KEY)
  },
  clear() {
    localStorage.removeItem(NAME_KEY)
    localStorage.removeItem(FARM_KEY)
  },
}
