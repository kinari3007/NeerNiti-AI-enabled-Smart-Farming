import { createContext, useContext } from 'react'

/**
 * Farm context + hook, kept separate from the provider component so that
 * React Fast Refresh works cleanly (a file should export only components
 * OR only non-components).
 */
export const FarmContext = createContext(null)

export function useFarm() {
  const ctx = useContext(FarmContext)
  if (!ctx) throw new Error('useFarm must be used within a FarmProvider')
  return ctx
}
