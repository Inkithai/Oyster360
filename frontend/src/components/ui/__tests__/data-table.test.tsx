import { fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { DataTable } from '../data-table'

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'quantity', label: 'Quantity' },
]
const data = [
  { name: 'Shiitake', quantity: 4 },
  { name: 'Blue Oyster', quantity: 12 },
  { name: 'Lion’s Mane', quantity: 7 },
]

describe('DataTable interactions', () => {
  const createObjectURL = vi.fn((blob: Blob) => {
    void blob
    return 'blob:csv'
  })
  const revokeObjectURL = vi.fn()

  beforeEach(() => {
    vi.stubGlobal('URL', { createObjectURL, revokeObjectURL })
  })

  afterEach(() => vi.unstubAllGlobals())

  it('filters rows and reports an empty result', () => {
    render(<DataTable data={data} columns={columns} />)

    fireEvent.change(screen.getByPlaceholderText('Search...'), { target: { value: 'blue' } })
    expect(screen.getByText('Blue Oyster')).toBeInTheDocument()
    expect(screen.queryByText('Shiitake')).not.toBeInTheDocument()

    fireEvent.change(screen.getByPlaceholderText('Search...'), { target: { value: 'missing' } })
    expect(screen.getByText('No results found.')).toBeInTheDocument()
  })

  it('sorts a column in both directions', () => {
    render(<DataTable data={data} columns={columns} />)
    const nameHeader = screen.getByRole('button', { name: 'Name' })

    fireEvent.click(nameHeader)
    let rows = screen.getAllByRole('row').slice(1)
    expect(within(rows[0]).getByText('Blue Oyster')).toBeInTheDocument()
    expect(nameHeader.closest('th')).toHaveAttribute('aria-sort', 'ascending')

    fireEvent.click(nameHeader)
    rows = screen.getAllByRole('row').slice(1)
    expect(within(rows[0]).getByText('Shiitake')).toBeInTheDocument()
    expect(nameHeader.closest('th')).toHaveAttribute('aria-sort', 'descending')
  })

  it('paginates without moving outside the available pages', () => {
    render(<DataTable data={data} columns={columns} pageSize={2} />)

    expect(screen.getByText('Page 1 of 2')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Previous page' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Next page' }))
    expect(screen.getByText('Page 2 of 2')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Next page' })).toBeDisabled()
    expect(screen.getByText('Lion’s Mane')).toBeInTheDocument()
  })

  it('exports the sorted, filtered rows as a CSV blob and releases its URL', () => {
    const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined)
    render(<DataTable data={data} columns={columns} />)
    fireEvent.change(screen.getByPlaceholderText('Search...'), { target: { value: 'oyster' } })
    fireEvent.click(screen.getByRole('button', { name: /Export CSV/i }))

    expect(createObjectURL).toHaveBeenCalledOnce()
    expect(createObjectURL.mock.calls[0][0]).toBeInstanceOf(Blob)
    expect(click).toHaveBeenCalledOnce()
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:csv')
    click.mockRestore()
  })
})
