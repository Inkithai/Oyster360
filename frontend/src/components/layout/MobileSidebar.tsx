'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Menu, Scale, X } from 'lucide-react'
import { navItems } from './Sidebar'
import { Locale, useI18n } from '@/lib/i18n'
import { cn } from '@/lib/utils'

const LANGUAGES: { code: Locale; label: string }[] = [
  { code: 'en', label: 'EN' },
  { code: 'si', label: 'සිං' },
  { code: 'ta', label: 'தமிழ்' },
]

export function MobileSidebar() {
  const [isOpen, setIsOpen] = useState(false)
  const pathname = usePathname()
  const { locale, setLocale, t } = useI18n()

  return (
    <>
      {/* Mobile Top Bar for inexpensive Android phones */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-40 flex items-center justify-between border-b bg-white px-4 py-2.5 shadow-xs">
        <button
          onClick={() => setIsOpen(true)}
          aria-label="Open navigation menu"
          className="p-2 rounded-lg border bg-white"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="font-semibold text-base">Oyster360</div>

        <Link
          href="/harvests/new"
          className="inline-flex items-center gap-1 rounded-lg bg-emerald-700 px-3 py-1.5 text-xs font-semibold text-white"
        >
          <Scale className="h-3.5 w-3.5" />
          + Harvest
        </Link>
      </div>

      {/* Mobile Drawer */}
      {isOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setIsOpen(false)}
          />

          <div className="absolute left-0 top-0 bottom-0 w-72 bg-white border-r p-6 overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <div className="font-semibold text-xl">Oyster360</div>
              <button onClick={() => setIsOpen(false)} aria-label="Close menu">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="flex items-center gap-1 rounded-lg border bg-gray-50 p-1 mb-4">
              {LANGUAGES.map((lang) => (
                <button
                  key={lang.code}
                  type="button"
                  onClick={() => setLocale(lang.code)}
                  className={cn(
                    'flex-1 rounded-md px-2 py-1.5 text-xs font-medium',
                    locale === lang.code
                      ? 'bg-black text-white'
                      : 'text-gray-700'
                  )}
                >
                  {lang.label}
                </button>
              ))}
            </div>

            <Link
              href="/harvests/new"
              onClick={() => setIsOpen(false)}
              className="mb-4 flex items-center justify-center gap-2 rounded-xl bg-emerald-700 px-4 py-3 text-sm font-semibold text-white"
            >
              <Scale className="h-4 w-4" />
              + {t('quickHarvest')}
            </Link>

            <nav className="space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setIsOpen(false)}
                    className={cn(
                      'flex items-center gap-3 px-4 py-3.5 rounded-xl text-sm font-medium',
                      isActive
                        ? 'bg-black text-white'
                        : 'text-gray-600 hover:bg-gray-100'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {locale === 'en' ? item.label : t(item.i18nKey)}
                  </Link>
                )
              })}
            </nav>
          </div>
        </div>
      )}
    </>
  )
}
