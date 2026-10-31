import { useCallback, useEffect, useRef, useState } from 'react'

/**
 * useAsync — runs an async function, tracking { data, loading, error }.
 *
 * @param fn            async function returning data
 * @param deps          dependency array; re-runs when these change
 * @param immediate     run on mount (default true)
 */
export function useAsync(fn, deps = [], immediate = true) {
  const [state, setState] = useState({
    data: null,
    loading: immediate,
    error: null,
  })
  const mounted = useRef(true)
  const fnRef = useRef(fn)

  // Keep the latest fn without reading/writing the ref during render.
  useEffect(() => {
    fnRef.current = fn
  }, [fn])

  useEffect(() => {
    mounted.current = true
    return () => {
      mounted.current = false
    }
  }, [])

  const run = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: null }))
    try {
      const data = await fnRef.current()
      if (mounted.current) setState({ data, loading: false, error: null })
      return data
    } catch (error) {
      if (mounted.current) setState({ data: null, loading: false, error })
      throw error
    }
  }, [])

  // Intentionally re-run only when the caller's deps change.
  /* eslint-disable react-hooks/set-state-in-effect, react-hooks/exhaustive-deps */
  useEffect(() => {
    if (immediate) run().catch(() => {})
  }, deps)
  /* eslint-enable react-hooks/set-state-in-effect, react-hooks/exhaustive-deps */

  return { ...state, reload: run, setData: (data) => setState((s) => ({ ...s, data })) }
}
