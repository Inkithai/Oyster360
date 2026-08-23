import path from 'node:path'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  esbuild: {
    jsx: 'automatic',
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    environment: 'jsdom',
    include: ['src/**/*.test.{ts,tsx}'],
    setupFiles: ['./vitest.setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      // Numeric gate enforced by `npm test -- --coverage` in CI (and locally
      // via `make verify`): any tracked surface below 60% fails the run.
      // Expand this list alongside each newly covered feature.
      include: [
        'src/app/dashboard/page.tsx',
        'src/app/forgot-password/page.tsx',
        'src/app/settings/subscription/page.tsx',
        'src/app/strains/page.tsx',
        'src/components/ErrorBoundary.tsx',
        'src/components/layout/Sidebar.tsx',
        'src/components/ui/data-table.tsx',
        'src/lib/logger.ts',
      ],
      thresholds: {
        lines: 60,
        statements: 60,
        functions: 60,
        branches: 60,
      },
    },
  },
})
