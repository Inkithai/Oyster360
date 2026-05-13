import { zodResolver } from "@hookform/resolvers/zod"
import { useForm, UseFormReturn } from "react-hook-form"
import { z } from "zod"

export function useZodForm<T extends z.ZodType>(
  schema: T,
  options?: {
    defaultValues?: z.infer<T>
    mode?: "onBlur" | "onChange" | "onSubmit"
  }
): UseFormReturn<z.infer<T>> {
  return useForm<z.infer<T>>({
    resolver: zodResolver(schema),
    defaultValues: options?.defaultValues,
    mode: options?.mode || "onBlur",
  })
}