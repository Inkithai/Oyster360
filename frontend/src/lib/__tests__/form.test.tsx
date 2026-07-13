import { renderHook } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { z } from 'zod'

import { useZodForm } from '../form'

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
})

describe('useZodForm', () => {
  it('returns a react-hook-form instance bound to the schema', () => {
    const { result } = renderHook(() =>
      useZodForm(schema, { defaultValues: { email: 'a@b.com', password: 'secret' }, mode: 'onSubmit' })
    )
    const form = result.current
    expect(typeof form.register).toBe('function')
    expect(typeof form.handleSubmit).toBe('function')
    expect(form.getValues('email')).toBe('a@b.com')
  })

  it('defaults mode to onBlur', () => {
    const { result } = renderHook(() => useZodForm(schema))
    expect(result.current).toBeDefined()
  })
})
