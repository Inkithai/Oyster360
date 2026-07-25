'use client'

import { ReactNode } from 'react'

type UserRole = 'ADMIN' | 'FARM_MANAGER' | 'WORKER' | 'VIEWER'

interface RoleGuardProps {
  allowedRoles: UserRole[]
  children: ReactNode
  fallback?: ReactNode
}

export function RoleGuard({ allowedRoles, children, fallback = null }: RoleGuardProps) {
  // In production, get role from JWT token or user context
  const userRole: UserRole = 'ADMIN' // TODO: Get from auth context
  
  if (allowedRoles.includes(userRole)) {
    return <>{children}</>
  }
  
  return <>{fallback}</>
}

// Role-specific components
export const AdminOnly = ({ children }: { children: ReactNode }) => (
  <RoleGuard allowedRoles={['ADMIN']}>{children}</RoleGuard>
)

export const ManagerOnly = ({ children }: { children: ReactNode }) => (
  <RoleGuard allowedRoles={['ADMIN', 'FARM_MANAGER']}>{children}</RoleGuard>
)

export const WorkerOnly = ({ children }: { children: ReactNode }) => (
  <RoleGuard allowedRoles={['ADMIN', 'FARM_MANAGER', 'WORKER']}>{children}</RoleGuard>
)