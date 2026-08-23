import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { ActiveBatchesTable } from '../ActiveBatchesTable'

describe('ActiveBatchesTable', () => {
  it('lists the active batches with their strain and growth stage', () => {
    render(<ActiveBatchesTable />)

    expect(screen.getByRole('heading', { name: 'Active Batches' })).toBeInTheDocument()
    expect(screen.getByText('B-2025-042')).toBeInTheDocument()
    expect(screen.getByText('Pearl Oyster')).toBeInTheDocument()
    expect(screen.getByText('COLONIZATION')).toBeInTheDocument()
    expect(screen.getByText('B-2025-043')).toBeInTheDocument()
    expect(screen.getByText('FRUITING')).toBeInTheDocument()
  })
})
