'use client'

import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { DataTable } from '@/components/ui/data-table'
import { useToast } from '@/components/ui/use-toast'

const BUYER_TYPES = [
  { value: 'RETAILER', label: 'Retailer / Supermarket' },
  { value: 'RESTAURANT', label: 'Restaurant / Cafe' },
  { value: 'WHOLESALER', label: 'Wholesaler / Pola Trader' },
  { value: 'HOTEL', label: 'Hotel / Catering' },
  { value: 'DIRECT_CUSTOMER', label: 'Direct Household Customer' },
  { value: 'INTERMEDIARY', label: 'Collector / Intermediary' },
]

export default function SalesPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const [buyerName, setBuyerName] = useState('')
  const [buyerType, setBuyerType] = useState('RETAILER')
  const [buyerPhone, setBuyerPhone] = useState('')
  const [buyerLocation, setBuyerLocation] = useState('')

  const [selectedBuyerId, setSelectedBuyerId] = useState('')
  const [quantityKg, setQuantityKg] = useState('')
  const [pricePerKgLkr, setPricePerKgLkr] = useState('650')
  const [amountPaidLkr, setAmountPaidLkr] = useState('')

  const { data: stock } = useQuery({
    queryKey: ['sales-stock'],
    queryFn: () => apiRequest('/api/sales/stock-summary'),
  })
  const { data: buyers = [] } = useQuery({
    queryKey: ['buyers'],
    queryFn: () => apiRequest('/api/sales/buyers'),
  })
  const { data: orders = [] } = useQuery({
    queryKey: ['sales-orders'],
    queryFn: () => apiRequest('/api/sales/orders'),
  })

  const refreshAll = () => {
    queryClient.invalidateQueries({ queryKey: ['sales-orders'] })
    queryClient.invalidateQueries({ queryKey: ['buyers'] })
    queryClient.invalidateQueries({ queryKey: ['sales-stock'] })
  }

  const createBuyerMutation = useMutation({
    mutationFn: () =>
      apiRequest('/api/sales/buyers', {
        method: 'POST',
        body: JSON.stringify({
          name: buyerName,
          buyer_type: buyerType,
          phone: buyerPhone,
          location: buyerLocation,
        }),
      }),
    onSuccess: (created) => {
      setBuyerName('')
      setBuyerPhone('')
      setBuyerLocation('')
      if (created?.id) setSelectedBuyerId(String(created.id))
      refreshAll()
      toast({ title: 'Buyer added', variant: 'success' })
    },
  })

  const createSaleMutation = useMutation({
    mutationFn: () => {
      const total = Number(quantityKg) * Number(pricePerKgLkr)
      const paid = amountPaidLkr === '' ? total : Number(amountPaidLkr)
      return apiRequest('/api/sales/orders', {
        method: 'POST',
        body: JSON.stringify({
          buyer_id: Number(selectedBuyerId || buyers[0]?.id),
          quantity_kg: Number(quantityKg),
          price_per_kg_lkr: Number(pricePerKgLkr),
          amount_paid_lkr: paid,
        }),
      })
    },
    onSuccess: () => {
      setQuantityKg('')
      setAmountPaidLkr('')
      refreshAll()
      toast({ title: 'Harvest sale recorded', variant: 'success' })
    },
    onError: (err: Error) => {
      toast({ title: err.message || 'Sale failed', variant: 'error' })
    },
  })

  const settlePaymentMutation = useMutation({
    mutationFn: ({ id, balance }: { id: number; balance: number }) =>
      apiRequest(`/api/sales/orders/${id}/payment`, {
        method: 'PATCH',
        body: JSON.stringify({ payment_amount_lkr: balance }),
      }),
    onSuccess: () => {
      refreshAll()
      toast({ title: 'Outstanding balance marked PAID', variant: 'success' })
    },
  })

  const buyerColumns = [
    { key: 'name', label: 'Buyer' },
    { key: 'buyer_type', label: 'Type' },
    { key: 'phone', label: 'Phone' },
    { key: 'location', label: 'Location' },
    { key: 'order_count', label: 'Repeat Orders' },
    { key: 'total_purchased_kg', label: 'Purchased (kg)' },
    {
      key: 'outstanding_balance_lkr',
      label: 'Balance Due (Rs.)',
      render: (item: any) => (
        <span className={item.outstanding_balance_lkr > 0 ? 'font-semibold text-red-600' : 'text-emerald-700'}>
          Rs. {Number(item.outstanding_balance_lkr || 0).toLocaleString()}
        </span>
      ),
    },
  ]

  const orderColumns = [
    { key: 'buyer_name', label: 'Buyer' },
    { key: 'quantity_kg', label: 'Qty (kg)' },
    { key: 'price_per_kg_lkr', label: 'Price/kg (Rs.)' },
    {
      key: 'total_amount_lkr',
      label: 'Total (Rs.)',
      render: (item: any) => `Rs. ${Number(item.total_amount_lkr || 0).toLocaleString()}`,
    },
    {
      key: 'balance_due_lkr',
      label: 'Balance Due (Rs.)',
      render: (item: any) => `Rs. ${Number(item.balance_due_lkr || 0).toLocaleString()}`,
    },
    {
      key: 'payment_status',
      label: 'Payment Status',
      render: (item: any) => (
        <div className="flex items-center gap-2">
          <span
            className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
              item.payment_status === 'PAID'
                ? 'bg-emerald-100 text-emerald-800'
                : item.payment_status === 'PARTIAL'
                ? 'bg-amber-100 text-amber-800'
                : 'bg-red-100 text-red-800'
            }`}
          >
            {item.payment_status}
          </span>
          {item.balance_due_lkr > 0 && (
            <button
              type="button"
              onClick={() => settlePaymentMutation.mutate({ id: item.id, balance: item.balance_due_lkr })}
              className="rounded border px-2 py-0.5 text-xs hover:bg-gray-100"
            >
              Mark Paid
            </button>
          )}
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Harvest Sales &amp; Buyer Management</h1>
        <p className="text-sm text-muted-foreground">
          Track sellable harvest stock, buyers, LKR payment status, and outstanding credit balances
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Available for Sale</CardTitle></CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-emerald-700">{stock?.available_for_sale_kg ?? 0} kg</div>
            <p className="text-xs text-muted-foreground mt-1">Harvested: {stock?.total_harvested_kg ?? 0} kg</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Total Sold</CardTitle></CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stock?.total_sold_kg ?? 0} kg</div>
            <p className="text-xs text-muted-foreground mt-1">Spoiled: {stock?.total_spoiled_kg ?? 0} kg</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Total Sales Revenue</CardTitle></CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">Rs. {Number(stock?.total_sales_lkr ?? 0).toLocaleString()}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Outstanding Balances</CardTitle></CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">
              Rs. {Number(stock?.outstanding_balance_lkr ?? 0).toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground mt-1">To collect from buyers</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>Record Harvest Sale (LKR)</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium">Buyer</label>
                <select value={selectedBuyerId} onChange={(e) => setSelectedBuyerId(e.target.value)} className="mt-1 w-full rounded-lg border px-3 py-2 text-sm">
                  <option value="">Select buyer</option>
                  {buyers.map((b: any) => <option key={b.id} value={b.id}>{b.name} ({b.buyer_type})</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs font-medium">Quantity Sold (kg)</label>
                <input type="number" step="0.5" value={quantityKg} onChange={(e) => setQuantityKg(e.target.value)} placeholder="e.g. 25" className="mt-1 w-full rounded-lg border px-3 py-2 text-sm" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium">Price per kg (Rs.)</label>
                <input type="number" value={pricePerKgLkr} onChange={(e) => setPricePerKgLkr(e.target.value)} className="mt-1 w-full rounded-lg border px-3 py-2 text-sm" />
              </div>
              <div>
                <label className="text-xs font-medium">Amount Paid Now (Rs.)</label>
                <input type="number" value={amountPaidLkr} onChange={(e) => setAmountPaidLkr(e.target.value)} placeholder="Blank = paid in full" className="mt-1 w-full rounded-lg border px-3 py-2 text-sm" />
              </div>
            </div>
            <Button onClick={() => createSaleMutation.mutate()} disabled={!quantityKg || (buyers.length === 0 && !selectedBuyerId)} className="w-full">
              Record Sale Order
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Add Buyer (Retailer, Restaurant, Wholesaler)</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium">Buyer Name</label>
                <input type="text" value={buyerName} onChange={(e) => setBuyerName(e.target.value)} placeholder="Keells Super — Maharagama" className="mt-1 w-full rounded-lg border px-3 py-2 text-sm" />
              </div>
              <div>
                <label className="text-xs font-medium">Buyer Type</label>
                <select value={buyerType} onChange={(e) => setBuyerType(e.target.value)} className="mt-1 w-full rounded-lg border px-3 py-2 text-sm">
                  {BUYER_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium">Phone</label>
                <input type="text" value={buyerPhone} onChange={(e) => setBuyerPhone(e.target.value)} placeholder="077-1234567" className="mt-1 w-full rounded-lg border px-3 py-2 text-sm" />
              </div>
              <div>
                <label className="text-xs font-medium">Town / Location</label>
                <input type="text" value={buyerLocation} onChange={(e) => setBuyerLocation(e.target.value)} placeholder="Maharagama / Pettah" className="mt-1 w-full rounded-lg border px-3 py-2 text-sm" />
              </div>
            </div>
            <Button variant="outline" onClick={() => createBuyerMutation.mutate()} disabled={buyerName.trim().length < 2} className="w-full">
              + Save Buyer
            </Button>
          </CardContent>
        </Card>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Buyers &amp; Repeat-Order Balances</h2>
        <DataTable data={buyers} columns={buyerColumns} searchable exportable />
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Sales Order History</h2>
        <DataTable data={orders} columns={orderColumns} searchable exportable />
      </div>
    </div>
  )
}
