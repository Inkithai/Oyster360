'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import {
  LayoutDashboard,
  Leaf,
  Scale,
  Calculator,
  Store,
  Package,
  BookOpen,
  Sprout,
  BarChart3,
  LogOut,
  Globe,
} from 'lucide-react'
import { apiRequest } from '@/lib/api'
import { Locale, useI18n } from '@/lib/i18n'
import { cn } from '@/lib/utils'

export const navItems = [
  { href: '/dashboard', label: 'Dashboard', i18nKey: 'dashboard', icon: LayoutDashboard },
  { href: '/batches', label: 'Batches', i18nKey: 'batches', icon: Leaf },
  { href: '/harvests', label: 'Harvests & Flushes', i18nKey: 'harvests', icon: Scale },
  { href: '/finance', label: 'Profit & Costs (LKR)', i18nKey: 'finance', icon: Calculator },
  { href: '/sales', label: 'Buyers & Sales', i18nKey: 'sales', icon: Store },
  { href: '/inventory', label: 'Inventory', i18nKey: 'inventory', icon: Package },
  { href: '/recipes', label: 'Recipes', i18nKey: 'recipes', icon: BookOpen },
  { href: '/strains', label: 'Strains', i18nKey: 'strains', icon: Sprout },
  { href: '/analytics', label: 'Analytics', i18nKey: 'analytics', icon: BarChart3 },
]

const LANGUAGES: { code: Locale; label: string }[] = [
  { code: 'en', label: 'EN' },
  { code: 'si', label: 'සිං' },
  { code: 'ta', label: 'தமிழ்' },
]

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { locale, setLocale, t } = useI18n()

  return (
    <div className="hidden md:flex w-64 flex-col border-r bg-muted/30 min-h-screen">
      <div className="p-6 border-b space-y-3">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-black flex items-center justify-center">
            <span className="text-white font-bold text-lg">O</span>
          </div>
          <div>
            <div className="font-semibold tracking-tight text-xl">Oyster360</div>
            <div className="text-[11px] text-muted-foreground -mt-1">{t('tagline')}</div>
          </div>
        </div>

        {/* Sinhala / Tamil / English Language Switcher */}
        <div className="flex items-center gap-1 rounded-lg border bg-white p-1" role="group" aria-label="Language selector">
          <Globe className="h-3.5 w-3.5 text-muted-foreground ml-1.5 mr-1" />
          {LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              type="button"
              onClick={() => setLocale(lang.code)}
              className={cn(
                'flex-1 rounded-md px-2 py-1 text-xs font-medium transition-colors',
                locale === lang.code
                  ? 'bg-black text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              )}
            >
              {lang.label}
            </button>
          ))}
        </div>
      </div>

      <div className="px-3 pt-4">
        <Link
          href="/harvests/new"
          className="flex items-center justify-center gap-2 rounded-xl bg-emerald-700 px-4 py-3 text-sm font-semibold text-white shadow-sm hover:bg-emerald-800 transition-colors"
        >
          <Scale className="h-4 w-4" />
          + {t('quickHarvest')}
        </Link>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all',
                isActive
                  ? 'bg-black text-white'
                  : 'text-gray-600 hover:text-black hover:bg-gray-100'
              )}
            >
              <Icon className="h-4 w-4" />
              {locale === 'en' ? item.label : t(item.i18nKey)}
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t mt-auto space-y-2">
        <button
          onClick={async () => {
            try {
              await apiRequest('/api/auth/logout', { method: 'POST' })
            } finally {
              localStorage.removeItem('token')
              localStorage.removeItem('refresh_token')
              router.push('/login')
            }
          }}
          className="w-full flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
        >
          <LogOut className="h-4 w-4" />
          Logout
        </button>

        <div className="text-xs text-gray-500 px-4 pt-2 border-t">
          Sri Lanka Grower Edition • LKR (Rs.)
        </div>
      </div>
    </div>
  )
}
