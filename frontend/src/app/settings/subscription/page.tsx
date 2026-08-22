'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/use-toast'

const PLANS = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    features: ['Up to 100 batches/month', 'Basic analytics', 'Email support']
  },
  {
    id: 'starter',
    name: 'Starter',
    price: 29,
    features: ['Up to 500 batches/month', 'AI Assistant', 'Image Analysis', 'Priority support']
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 99,
    features: ['Unlimited batches', 'Advanced Analytics', 'Team Management', 'API Access', 'Dedicated support']
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 299,
    features: ['Everything in Pro', 'Custom Integrations', 'SLA', 'Dedicated Account Manager', 'On-premise option']
  }
]

export default function SubscriptionPage() {
  const { toast } = useToast()
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)

  const { data: subscription } = useQuery({
    queryKey: ['subscription'],
    queryFn: () => apiRequest('/api/billing/subscription'),
  })

  const createCheckout = useMutation({
    mutationFn: (plan: string) =>
      apiRequest('/api/billing/create-checkout-session', {
        method: 'POST',
        body: JSON.stringify({
          plan,
          success_url: `${window.location.origin}/settings/subscription?success=true`,
          cancel_url: `${window.location.origin}/settings/subscription?canceled=true`
        })
      }),
    onSuccess: (data) => {
      // Redirect to Stripe Checkout
      window.location.href = data.checkout_url
    },
    onError: () => {
      toast({ title: 'Failed to start checkout', variant: 'error' })
    }
  })

  const cancelSubscription = useMutation({
    mutationFn: () => apiRequest('/api/billing/cancel-subscription', {
      method: 'POST'
    }),
    onSuccess: () => {
      toast({ title: 'Subscription will cancel at period end', variant: 'success' })
    }
  })

  const handleUpgrade = (planId: string) => {
    setSelectedPlan(planId)
    createCheckout.mutate(planId)
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold tracking-tight">Subscription</h1>
        <p className="text-muted-foreground">Manage your Oyster360 subscription</p>
      </div>

      {subscription && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Current Plan: {subscription.plan}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center">
              <div>
                <div>Status: <span className="font-medium">{subscription.status}</span></div>
                <div>Renews: {new Date(subscription.current_period_end).toLocaleDateString()}</div>
              </div>
              <Button 
                variant="destructive" 
                onClick={() => cancelSubscription.mutate()}
                disabled={subscription.cancel_at_period_end}
              >
                {subscription.cancel_at_period_end ? 'Cancellation Scheduled' : 'Cancel Subscription'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {PLANS.map((plan) => (
          <Card key={plan.id} className={selectedPlan === plan.id ? 'ring-2 ring-primary' : ''}>
            <CardHeader>
              <CardTitle>{plan.name}</CardTitle>
              <div className="text-3xl font-bold">
                ${plan.price}
                <span className="text-sm font-normal">/month</span>
              </div>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 mb-6">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-center text-sm">
                    <span className="text-green-500 mr-2">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>
              <Button 
                className="w-full"
                variant={subscription?.plan === plan.id ? "outline" : "default"}
                onClick={() => handleUpgrade(plan.id)}
                disabled={subscription?.plan === plan.id}
              >
                {subscription?.plan === plan.id ? 'Current Plan' : 'Upgrade'}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}