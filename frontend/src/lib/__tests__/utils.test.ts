import { describe, expect, it } from 'vitest'

import { cn } from '../utils'

describe('cn (className merge)', () => {
  it('joins conditional class values', () => {
    expect(cn('a', false && 'b', 'c')).toBe('a c')
  })

  it('dedupes conflicting tailwind utilities (last wins)', () => {
    expect(cn('p-2', 'p-4')).toBe('p-4')
  })

  it('handles empty input', () => {
    expect(cn()).toBe('')
  })
})
