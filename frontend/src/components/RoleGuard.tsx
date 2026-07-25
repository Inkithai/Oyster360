'use client'

import { ReactNode, useSyncExternalStore } from 'react'

type UserRole = 'ADMIN' | 'FARM_MANAGER' | 'WORKER' | 'VIEWER'

interface RoleGuardProps {
  allowedRoles: UserRole[]
  children: ReactNode
  fallback?: ReactNode
}

const USER_ROLES = new Set<UserRole>([
  'ADMIN',
  'FARM_MANAGER',
  'WORKER',
  'VIEWER',
])

function roleFromAccessToken(token: string | null): UserRole | null {
  if (!token) return null

  try {
    const encodedPayload = token.split('.')[1]
    if (!encodedPayload) return null
    const base64 = encodedPayload.replace(/-/g, '+').replace(/_/g, '/')
    const payload = JSON.parse(atob(base64)) as { role?: string }
    return payload.role && USER_ROLES.has(payload.role as UserRole)
      ? payload.role as UserRole
      : null
  } catch {
    return null
  }
}

function subscribeToTokenChanges(onStoreChange: () => void) {
  window.addEventListener('storage', onStoreChange)
  return () => window.removeEventListener('storage', onStoreChange)
}

function getTokenSnapshot() {
  return localStorage.getItem('token') || ''
}

export function RoleGuard({ allowedRoles, children, fallback = null }: RoleGuardProps) {
  const token = useSyncExternalStore(subscribeToTokenChanges, getTokenSnapshot, () => '')
  const userRole = roleFromAccessToken(token)

  if (userRole && allowedRoles.includes(userRole)) {
    return <>{children}</>
  }

  return <>{fallback}</>
}

export const AdminOnly = ({ children }: { children: ReactNode }) => (
  <RoleGuard allowedRoles={['ADMIN']}>{children}</RoleGuard>
)

export const ManagerOnly = ({ children }: { children: ReactNode }) => (
  <RoleGuard allowedRoles={['ADMIN', 'FARM_MANAGER']}>{children}</RoleGuard>
)

export const WorkerOnly = ({ children }: { children: ReactNode }) => (
  <RoleGuard allowedRoles={['ADMIN', 'FARM_MANAGER', 'WORKER']}>{children}</RoleGuard>
)
