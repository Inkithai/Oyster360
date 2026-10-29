'use client'

import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { DataTable } from '@/components/ui/data-table'
import { useToast } from '@/components/ui/use-toast'

const EXPENSE_CATEGORIES = [
  { value: 'SUBSTRATE', label: 'Substrate (Sawdust, Rice Bran, Lime, MgSO4)' },
  { value: 'SPAWN', label: 'Spawn (Grain / Paddy Spawn Bottles)' },
  { value: 'BAGS', label: 'Polypropylene Bags, Rings & Cotton Plugs' },
  { value: 'PACKAGING', label: 'Retail Packaging & Labels' },
  { value: 'ELECTRICITY', label: 'Electricity & Steaming Fuel / Firewood' },
  { value: 'WATER', label: 'Water & Misting' },
  { value: 'LABOUR', label: 'Labour & Helper Wages' },
  { value: 'TRANSPORT', label: 'Transport & Delivery' },
  { value: 'OTHER', label: 'Other Farm Expenses' },
]

export default function FinancePage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const [category, setCategory] = useState('SUBSTRATE')
  const [amountLkr, setAmountLkr] = useState('')
  const [description, setDescription] = useState('')
  const [batchId, setBatchId] = useState('')

  const { data: summary } = useQuery({
    queryKey: ['profitability'],
    queryFn: () => apiRequest('/api/finance/profitability'),
  })

  const { data: expenses = [] } = useQuery({
    queryKey: ['expenses'],
    queryFn: () => apiRequest('/api/finance/expenses'),
  })

  const recordExpense = useMutation({
    mutationFn: () =>
      apiRequest('/api/finance/expenses', {
        method: 'POST',
        body: JSON.stringify({
          category,
          amount_lkr: Number(amountLkr),
          description,
          batch_id: batchId ? Number(batchId) : null,
        }),
      }),
    onSuccess: () => {
      setAmountLkr('')
      setDescription('')
      queryClient.invalidateQueries({ queryKey: ['profitability'] })
      queryClient.invalidateQueries({ queryKey: ['expenses'] })
      toast({ title: 'Expense recorded in LKR', variant: 'success' })
    },
    onError: (err: Error) => {
      toast({ title: err.message || 'Failed to record expense', variant: 'error' })
    },
  })

  const batchColumns = [
    { key: 'batch_number', label: 'Batch' },
    { key: 'bags_prepared', label: 'Bags' },
    { key: 'expected_yield_kg', label: 'Expected (kg)' },
    { key: 'actual_yield_kg', label: 'Actual (kg)' },
    {
      key: 'cost_per_bag_lkr',
      label: 'Cost/Bag (Rs.)',
      render: (item: any) => `Rs. ${Number(item.cost_per_bag_lkr || 0).toLocaleString()}`,
    },
    {
      key: 'total_cost_lkr',
      label: 'Total Cost (Rs.)',
      render: (item: any) => `Rs. ${Number(item.total_cost_lkr || 0).toLocaleString()}`,
    },
    {
      key: 'revenue_lkr',
      label: 'Revenue (Rs.)',
      render: (item: any) => `Rs. ${Number(item.revenue_lkr || 0).toLocaleString()}`,
    },
    {
      key: 'net_profit_lkr',
      label: 'Net Profit (Rs.)',
      render: (item: any) => (
        <span className={item.net_profit_lkr >= 0 ? 'font-semibold text-emerald-700' : 'font-semibold text-red-600'}>
          Rs. {Number(item.net_profit_lkr || 0).toLocaleString()}
        </span>
      ),
    },
  ]

  const expenseColumns = [
    { key: 'category', label: 'Category' },
    { key: 'description', label: 'Description' },
    {
      key: 'amount_lkr',
      label: 'Amount (Rs.)',
      render: (item: any) => `Rs. ${Number(item.amount_lkr || 0).toLocaleString()}`,
    },
    {
      key: 'expense_date',
      label: 'Date',
      render: (item: any) => (item.expense_date ? new Date(item.expense_date).toLocaleDateString() : '-'),
    },
  ]

  const netProfit = summary?.estimated_net_profit_lkr ?? 0
  const grossProfit = summary?.gross_profit_lkr ?? 0

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Profit &amp; Cost Calculator (LKR)</h1>
          <p className="text-sm text-muted-foreground">
            Track expenses in Sri Lankan Rupees (Rs.) and measure cost per grow bag, cost per kg, and net profit
          </p>
        </div>
        <Button variant="outline" onClick={() => window.print()}>
          Print Monthly Report
        </Button>
      </div>

      {/* Profitability KPIs in LKR */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Estimated Net Profit</CardTitle></CardHeader>
          <CardContent>
            <div className={`text-2xl md:text-3xl font-bold ${netProfit >= 0 ? 'text-emerald-700' : 'text-red-600'}`}>
              Rs. {Number(netProfit).toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Gross Profit: Rs. {Number(grossProfit).toLocaleString()}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Cost per Grow Bag &amp; kg</CardTitle></CardHeader>
          <CardContent>
            <div className="text-2xl md:text-3xl font-bold">
              Rs. {summary?.cost_per_bag_lkr ?? 0} <span className="text-sm font-normal text-muted-foreground">/bag</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Cost per kg: Rs. {summary?.cost_per_kg_lkr ?? 0}/kg
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Profit per Kilogram</CardTitle></CardHeader>
          <CardContent>
            <div className="text-2xl md:text-3xl font-bold text-emerald-700">
              Rs. {summary?.profit_per_kg_lkr ?? 0} <span className="text-sm font-normal text-muted-foreground">/kg</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Margin: {summary?.profit_margin_pct ?? 0}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Actual vs Expected Yield</CardTitle></CardHeader>
          <CardContent>
            <div className="text-2xl md:text-3xl font-bold">
              {summary?.total_harvested_kg ?? 0} / {summary?.expected_yield_kg ?? 0} kg
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Yield Efficiency: {summary?.yield_efficiency_pct ?? 0}%
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Record Expense Form */}
      <Card>
        <CardHeader>
          <CardTitle>Record Farm Expense (LKR)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="text-xs font-medium">Expense Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="mt-1 w-full rounded-lg border px-3 py-2.5 text-sm"
              >
                {EXPENSE_CATEGORIES.map((c) => (
                  <option key={c.value} value={c.value}>{c.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium">Amount (Rs. / LKR)</label>
              <input
                type="number"
                min={1}
                value={amountLkr}
                onChange={(e) => setAmountLkr(e.target.value)}
                placeholder="e.g. 12500"
                className="mt-1 w-full rounded-lg border px-3 py-2.5 text-sm"
              />
            </div>
            <div>
              <label className="text-xs font-medium">Description</label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g. 100kg sawdust + 10kg rice bran"
                className="mt-1 w-full rounded-lg border px-3 py-2.5 text-sm"
              />
            </div>
            <div>
              <label className="text-xs font-medium">Batch ID (Optional)</label>
              <div className="mt-1 flex gap-2">
                <input
                  type="number"
                  value={batchId}
                  onChange={(e) => setBatchId(e.target.value)}
                  placeholder="Farm-wide"
                  className="w-28 rounded-lg border px-3 py-2.5 text-sm"
                />
                <Button
                  onClick={() => recordExpense.mutate()}
                  disabled={!amountLkr || Number(amountLkr) <= 0 || recordExpense.isPending}
                  className="flex-1"
                >
                  Save Expense
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div>
        <h2 className="text-xl font-semibold mb-4">Profit by Batch &amp; Cultivation Cycle</h2>
        <DataTable data={summary?.batch_profitability ?? []} columns={batchColumns} searchable exportable />
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Expense History (LKR)</h2>
        <DataTable data={expenses} columns={expenseColumns} searchable exportable />
      </div>
    </div>
  )
}
