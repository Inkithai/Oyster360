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
      // Coverage is deliberately scoped to the interactive production surface
      // that has behavior tests. Add a source file here together with its test.
      include: [
        'src/app/batches/page.tsx',
        'src/app/dashboard/page.tsx',
        'src/app/inventory/page.tsx',
        'src/components/batches/ActiveBatchesTable.tsx',
        'src/components/layout/Sidebar.tsx',
        'src/components/ui/data-table.tsx',
      ],
      thresholds: {
        lines: 70,
        statements: 70,
        functions: 70,
        branches: 60,
      },
    },
  },
})
