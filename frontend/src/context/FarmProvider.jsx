import { useCallback, useEffect, useState } from 'react'
import { farmsApi } from '../api/farms'
import { session } from '../api/session'
import { FarmContext } from './farm-context'

/**
 * FarmProvider — loads the farmer's farms once and tracks the active farm.
 * Shared across all authenticated pages so they agree on which farm is selected.
 *
 * The `useFarm` hook lives in ./farm-context so this file only exports a component.
 */
export function FarmProvider({ children }) {
  const [farms, setFarms] = useState([])
  const [activeFarmId, setActiveFarmIdState] = useState(session.getActiveFarmId())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadFarms = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await farmsApi.list(1, 100)
      const items = res?.items || []
      setFarms(items)

      // Reconcile active farm: keep if still valid, else pick first, else none.
      const stored = session.getActiveFarmId()
      const validStored = items.find((f) => f.id === stored)
      const next = validStored ? stored : items[0]?.id || ''
      setActiveFarmIdState(next)
      session.setActiveFarmId(next)
      return items
    } catch (err) {
      setError(err)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    // Load the farmer's farms once on mount.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadFarms().catch(() => {})
  }, [loadFarms])

  const setActiveFarmId = useCallback((id) => {
    setActiveFarmIdState(id)
    session.setActiveFarmId(id)
  }, [])

  const activeFarm = farms.find((f) => f.id === activeFarmId) || null

  const value = {
    farms,
    activeFarm,
    activeFarmId,
    setActiveFarmId,
    loading,
    error,
    reloadFarms: loadFarms,
    hasFarms: farms.length > 0,
  }

  return <FarmContext.Provider value={value}>{children}</FarmContext.Provider>
}
