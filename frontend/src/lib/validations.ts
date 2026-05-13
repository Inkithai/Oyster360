import { z } from "zod"

export const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
})

export const batchSchema = z.object({
  batch_number: z.string().min(1, "Batch number is required"),
  strain_id: z.number().min(1, "Please select a strain"),
  recipe_version_id: z.number().min(1, "Please select a recipe"),
  room_id: z.number().min(1, "Please select a room"),
})

export const recipeSchema = z.object({
  name: z.string().min(1, "Recipe name is required"),
  description: z.string().optional(),
  hydration_percentage: z.number().min(0).max(100),
  spawn_ratio: z.number().min(1).max(20),
})

export type LoginForm = z.infer<typeof loginSchema>
export type BatchForm = z.infer<typeof batchSchema>
export type RecipeForm = z.infer<typeof recipeSchema>