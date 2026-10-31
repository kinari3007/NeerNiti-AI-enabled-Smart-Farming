import { describe, it, expect } from 'vitest'
import {
  formatMoney,
  formatNumber,
  formatPercent,
  formatDate,
  formatDateTime,
  safeJsonParse,
} from './format'

describe('formatMoney', () => {
  it('formats INR with the rupee symbol', () => {
    expect(formatMoney(6075.54, 'INR')).toBe('₹6,075.54')
  })
  it('formats USD with a dollar symbol', () => {
    expect(formatMoney(100, 'USD')).toBe('$100')
  })
  it('falls back to a dash for null/NaN', () => {
    expect(formatMoney(null)).toBe('—')
    expect(formatMoney(NaN)).toBe('—')
  })
})

describe('formatNumber', () => {
  it('rounds to the given digits', () => {
    expect(formatNumber(104.915, 1)).toBe('104.9')
  })
  it('returns a dash for null', () => {
    expect(formatNumber(null)).toBe('—')
  })
})

describe('formatPercent', () => {
  it('converts a 0..1 fraction to a percent string', () => {
    expect(formatPercent(0.87)).toBe('87%')
    expect(formatPercent(1)).toBe('100%')
  })
  it('returns null for null/NaN (so callers can hide it honestly)', () => {
    expect(formatPercent(null)).toBeNull()
    expect(formatPercent(NaN)).toBeNull()
  })
})

describe('formatDate / formatDateTime', () => {
  it('returns a dash for empty input', () => {
    expect(formatDate('')).toBe('—')
    expect(formatDateTime(null)).toBe('—')
  })
  it('returns a dash for invalid dates', () => {
    expect(formatDate('not-a-date')).toBe('—')
  })
  it('formats a valid ISO date to a non-empty string', () => {
    const out = formatDate('2026-10-21T08:00:00Z')
    expect(out).not.toBe('—')
    expect(out.length).toBeGreaterThan(0)
  })
})

describe('safeJsonParse', () => {
  it('parses valid JSON', () => {
    expect(safeJsonParse('{"a":1}')).toEqual({ a: 1 })
  })
  it('returns the fallback on invalid JSON', () => {
    expect(safeJsonParse('{bad', [])).toEqual([])
  })
  it('returns the fallback for empty input', () => {
    expect(safeJsonParse('', null)).toBeNull()
  })
})
