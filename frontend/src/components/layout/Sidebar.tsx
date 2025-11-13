'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { 
  LayoutDashboard, 
  Leaf, 
  BookOpen, 
  BarChart3, 
  Users,
  Package,
  ShoppingCart,
  Award,
  MessageCircle,
  Camera,
  LogOut
} from 'lucide-react'
import { apiRequest } from '@/lib/api'
import { cn } from '@/lib/utils'

export const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/batches', label: 'Batches', icon: Leaf },
  { href: '/recipes', label: 'Recipes', icon: BookOpen },
  { href: '/inventory', label: 'Inventory', icon: Package },
  { href: '/purchases', label: 'Purchases', icon: ShoppingCart },
  { href: '/grading', label: 'Quality Control', icon: Award },
  { href: '/analytics', label: 'Analytics', icon: BarChart3 },
  { href: '/assistant', label: 'AI Assistant', icon: MessageCircle },
  { href: '/analysis', label: 'Image Analysis', icon: Camera },
  { href: '/strains', label: 'Strains', icon: Users },
]

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()

  return (
    <div className="hidden md:flex w-64 flex-col border-r bg-muted/30 min-h-screen">
      <div className="p-6 border-b">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-black flex items-center justify-center">
            <span className="text-white font-bold text-lg">O</span>
          </div>
          <div>
            <div className="font-semibold tracking-tight text-xl">Oyster360</div>
            <div className="text-[10px] text-muted-foreground -mt-1">Farm Intelligence</div>
          </div>
        </div>
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
                "flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all",
                isActive 
                  ? "bg-black text-white" 
                  : "text-gray-600 hover:text-black hover:bg-gray-100"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
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
          v1.0.0 • Production
        </div>
      </div>
    </div>
  )
}