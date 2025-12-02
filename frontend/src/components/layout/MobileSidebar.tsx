'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Menu, X } from 'lucide-react'
import { navItems } from './Sidebar'
import { cn } from '@/lib/utils'

export function MobileSidebar() {
  const [isOpen, setIsOpen] = useState(false)
  const pathname = usePathname()

  return (
    <>
      {/* Hamburger Button */}
      <button 
        onClick={() => setIsOpen(true)} 
        className="md:hidden fixed top-4 left-4 z-50 p-2 rounded-lg border bg-white"
      >
        <Menu className="h-5 w-5" />
      </button>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div 
            className="absolute inset-0 bg-black/50" 
            onClick={() => setIsOpen(false)} 
          />
          
          <div className="absolute left-0 top-0 bottom-0 w-72 bg-white border-r p-6">
            <div className="flex justify-between items-center mb-8">
              <div className="font-semibold text-xl">Oyster360</div>
              <button onClick={() => setIsOpen(false)}>
                <X className="h-5 w-5" />
              </button>
            </div>

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
                      "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium",
                      isActive 
                        ? "bg-black text-white" 
                        : "text-gray-600 hover:bg-gray-100"
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
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