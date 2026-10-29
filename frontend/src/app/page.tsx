'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { ArrowRight, Calculator, Scale, ShieldAlert, Sprout, Store, Smartphone } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navbar */}
      <nav className="border-b">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-black flex items-center justify-center">
              <span className="text-white font-bold text-lg">O</span>
            </div>
            <div>
              <span className="font-semibold text-2xl tracking-tight">Oyster360</span>
              <span className="ml-2 rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-medium text-emerald-800">
                Sri Lanka Edition
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/register">
              <Button>Start Free</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-5xl mx-auto px-6 pt-16 pb-14 text-center">
        <div className="inline-block px-4 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-900 text-sm mb-6">
          Built for Sri Lankan Mushroom Growers • සිංහල • தமிழ் • English
        </div>

        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
          Track grow bags, record harvests,<br />and know your real profit in Rs.
        </h1>

        <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-10">
          Oyster360 helps Sri Lankan mushroom growers track grow bags, record harvests,
          understand their costs, and know how much profit their farm actually makes.
        </p>

        <div className="flex flex-wrap justify-center gap-4">
          <Link href="/register">
            <Button size="lg" className="px-8">
              Set Up Your Farm <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button variant="outline" size="lg" className="px-8">
              Open Farm Dashboard
            </Button>
          </Link>
        </div>
      </div>

      {/* Six Commercial Differentiators for Sri Lankan Growers */}
      <div className="max-w-7xl mx-auto px-6 py-16 border-t">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="rounded-2xl border p-6">
            <div className="w-11 h-11 rounded-xl bg-emerald-100 flex items-center justify-center mb-4">
              <Scale className="h-5 w-5 text-emerald-800" />
            </div>
            <h3 className="font-semibold text-lg mb-2">60-Second Harvest Entry</h3>
            <p className="text-sm text-muted-foreground">
              Record daily harvest weight per batch and per flush in kilograms or grams in a few taps—faster than writing in a notebook.
            </p>
          </div>

          <div className="rounded-2xl border p-6">
            <div className="w-11 h-11 rounded-xl bg-emerald-100 flex items-center justify-center mb-4">
              <Calculator className="h-5 w-5 text-emerald-800" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Real Profit &amp; Cost per kg (LKR)</h3>
            <p className="text-sm text-muted-foreground">
              Track sawdust, rice bran, spawn, bags, packaging, electricity, labour, and transport in Rs. to see exact cost per bag and net profit per kg.
            </p>
          </div>

          <div className="rounded-2xl border p-6">
            <div className="w-11 h-11 rounded-xl bg-emerald-100 flex items-center justify-center mb-4">
              <Store className="h-5 w-5 text-emerald-800" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Buyer &amp; Payment Collection</h3>
            <p className="text-sm text-muted-foreground">
              Manage supermarkets, restaurants, wholesalers, hotels, and direct buyers with payment status, outstanding balances, and unsold/spoiled stock.
            </p>
          </div>

          <div className="rounded-2xl border p-6">
            <div className="w-11 h-11 rounded-xl bg-emerald-100 flex items-center justify-center mb-4">
              <ShieldAlert className="h-5 w-5 text-emerald-800" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Grow-Bag &amp; Crop-Loss Visibility</h3>
            <p className="text-sm text-muted-foreground">
              Track bags prepared, inoculated, contaminated, and harvested for every batch, with automatic alerts when contamination exceeds 10%.
            </p>
          </div>

          <div className="rounded-2xl border p-6">
            <div className="w-11 h-11 rounded-xl bg-emerald-100 flex items-center justify-center mb-4">
              <Sprout className="h-5 w-5 text-emerald-800" />
            </div>
            <h3 className="font-semibold text-lg mb-2">DOA Sri Lanka Varieties &amp; Guide</h3>
            <p className="text-sm text-muted-foreground">
              Pre-configured for American Oyster (Bhutani), Abalone, Pink Oyster, and Milky Mushroom with Department of Agriculture stage checklists.
            </p>
          </div>

          <div className="rounded-2xl border p-6">
            <div className="w-11 h-11 rounded-xl bg-emerald-100 flex items-center justify-center mb-4">
              <Smartphone className="h-5 w-5 text-emerald-800" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Mobile-First &amp; Trilingual</h3>
            <p className="text-sm text-muted-foreground">
              Large buttons, short forms, CSV export, and Sinhala, Tamil, and English labels built for everyday Android phones inside the farm.
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t py-8 text-center text-sm text-muted-foreground">
        © 2026 Oyster360 • Practical Mushroom-Farm Management for Sri Lankan Growers
      </footer>
    </div>
  )
}
