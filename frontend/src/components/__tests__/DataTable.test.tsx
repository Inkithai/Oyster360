import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { DataTable } from '../ui/data-table'

describe('DataTable', () => {
  const mockData = [
    { id: 1, name: 'Test 1', status: 'active' },
    { id: 2, name: 'Test 2', status: 'inactive' }
  ]

  const mockColumns = [
    { key: 'name', label: 'Name' },
    { key: 'status', label: 'Status' }
  ]

  it('renders table with data', () => {
    render(<DataTable data={mockData} columns={mockColumns} />)
    expect(screen.getByText('Test 1')).toBeInTheDocument()
    expect(screen.getByText('Test 2')).toBeInTheDocument()
  })

  it('shows empty state when no data', () => {
    render(<DataTable data={[]} columns={mockColumns} />)
    expect(screen.getByText('No results found.')).toBeInTheDocument()
  })
})