'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { ArrowRight, CheckCircle, Zap, Users, BarChart3 } from 'lucide-react'

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
            <span className="font-semibold text-2xl tracking-tight">Oyster360</span>
          </div>
          
          <div className="flex items-center gap-4">
            <Link href="/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/register">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-5xl mx-auto px-6 pt-20 pb-16 text-center">
        <div className="inline-block px-4 py-1.5 rounded-full bg-muted text-sm mb-6">
          AI-Powered Oyster Mushroom Farming
        </div>
        
        <h1 className="text-6xl font-bold tracking-tighter mb-6">
          Run your oyster farm<br />with intelligence
        </h1>
        
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
          Oyster360 helps commercial oyster mushroom farms increase yield, 
          reduce contamination, and make data-driven decisions.
        </p>

        <div className="flex justify-center gap-4">
          <Link href="/register">
            <Button size="lg" className="px-8">
              Start Free Trial <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
          <Link href="/login">
            <Button variant="outline" size="lg" className="px-8">
              Watch Demo
            </Button>
          </Link>
        </div>
      </div>

      {/* Features */}
      <div className="max-w-7xl mx-auto px-6 py-20 border-t">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              <Zap className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold text-xl mb-2">AI Cultivation Assistant</h3>
            <p className="text-muted-foreground">
              Get instant recommendations based on your farm data and oyster mushroom best practices.
            </p>
          </div>

          <div className="text-center">
            <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              <BarChart3 className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold text-xl mb-2">Yield Prediction</h3>
            <p className="text-muted-foreground">
              Predict harvest dates and quantities with high confidence using environmental data.
            </p>
          </div>

          <div className="text-center">
            <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              <Users className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold text-xl mb-2">Team Collaboration</h3>
            <p className="text-muted-foreground">
              Role-based access for owners, managers, and workers with mobile-friendly interfaces.
            </p>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="border-t py-16">
        <div className="max-w-2xl mx-auto text-center px-6">
          <h2 className="text-3xl font-bold tracking-tight mb-4">
            Ready to optimize your farm?
          </h2>
          <p className="text-muted-foreground mb-8">
            Join oyster mushroom farms using Oyster360 to improve yield and reduce losses.
          </p>
          <Link href="/register">
            <Button size="lg">
              Get Started Free
            </Button>
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t py-8 text-center text-sm text-muted-foreground">
        © 2026 Oyster360. Built for oyster mushroom farmers.
      </footer>
    </div>
  )
}