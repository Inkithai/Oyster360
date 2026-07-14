import { describe, expect, it } from 'vitest'

import { batchSchema, loginSchema, recipeSchema } from '../validations'

describe('loginSchema', () => {
  it('accepts a valid login', () => {
    const result = loginSchema.safeParse({ email: 'a@b.com', password: 'secret1' })
    expect(result.success).toBe(true)
  })

  it('rejects an invalid email', () => {
    expect(loginSchema.safeParse({ email: 'not-an-email', password: 'secret1' }).success).toBe(false)
  })

  it('rejects a short password', () => {
    expect(loginSchema.safeParse({ email: 'a@b.com', password: '12345' }).success).toBe(false)
  })
})

describe('batchSchema', () => {
  it('requires all positive ids', () => {
    expect(
      batchSchema.safeParse({ batch_number: 'B-1', strain_id: 1, recipe_version_id: 1, room_id: 1 }).success
    ).toBe(true)
  })

  it('fails when batch_number is empty', () => {
    expect(
      batchSchema.safeParse({ batch_number: '', strain_id: 1, recipe_version_id: 1, room_id: 1 }).success
    ).toBe(false)
  })

  it('fails when strain_id is not selected (0)', () => {
    expect(
      batchSchema.safeParse({ batch_number: 'B-1', strain_id: 0, recipe_version_id: 1, room_id: 1 }).success
    ).toBe(false)
  })
})

describe('recipeSchema', () => {
  it('accepts a valid recipe', () => {
    expect(
      recipeSchema.safeParse({ name: 'Oyster', hydration_percentage: 60, spawn_ratio: 3 }).success
    ).toBe(true)
  })

  it('rejects hydration outside 0-100', () => {
    expect(
      recipeSchema.safeParse({ name: 'Oyster', hydration_percentage: 150, spawn_ratio: 3 }).success
    ).toBe(false)
  })

  it('rejects spawn_ratio outside 1-20', () => {
    expect(
      recipeSchema.safeParse({ name: 'Oyster', hydration_percentage: 60, spawn_ratio: 25 }).success
    ).toBe(false)
  })
})
