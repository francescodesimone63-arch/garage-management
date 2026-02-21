import { useContext } from 'react'
import { AuthContext } from '../contexts/AuthContext'

/**
 * Custom hook to check if the current user has a specific permission
 *
 * @param permission - Permission code to check (e.g., 'customers.create', 'vehicles.delete')
 * @returns boolean - true if user has the permission, false otherwise
 *
 * @example
 * const canCreateCustomer = usePermission('customers.create')
 * const canDeleteVehicle = usePermission('vehicles.delete')
 *
 * return (
 *   <>
 *     {canCreateCustomer && <Button onClick={handleCreate}>Create</Button>}
 *     {canDeleteVehicle && <Button onClick={handleDelete}>Delete</Button>}
 *   </>
 * )
 */
export const usePermission = (permission: string): boolean => {
  const authContext = useContext(AuthContext)

  if (!authContext) {
    console.warn('usePermission must be used within AuthProvider')
    return false
  }

  const { user, permissions } = authContext

  // If user is not logged in
  if (!user || !permissions) {
    return false
  }

  // Admin users have all permissions
  if (user.ruolo === 'ADMIN') {
    return true
  }

  // Check if permission exists in user's permissions array
  return permissions.includes(permission)
}

/**
 * Custom hook to check if the current user has ANY of the given permissions
 *
 * @param permissions - Array of permission codes to check
 * @returns boolean - true if user has at least one of the permissions
 *
 * @example
 * const canManageContent = usePermissionAny(['customers.create', 'customers.edit'])
 */
export const usePermissionAny = (permissionList: string[]): boolean => {
  const authContext = useContext(AuthContext)

  if (!authContext) {
    console.warn('usePermissionAny must be used within AuthProvider')
    return false
  }

  const { user, permissions } = authContext

  if (!user || !permissions) {
    return false
  }

  if (user.ruolo === 'ADMIN') {
    return true
  }

  return permissionList.some((p) => permissions.includes(p))
}

/**
 * Custom hook to check if the current user has ALL of the given permissions
 *
 * @param permissions - Array of permission codes to check
 * @returns boolean - true if user has all of the permissions
 *
 * @example
 * const canManageAll = usePermissionAll(['customers.create', 'customers.delete', 'customers.approve'])
 */
export const usePermissionAll = (permissionList: string[]): boolean => {
  const authContext = useContext(AuthContext)

  if (!authContext) {
    console.warn('usePermissionAll must be used within AuthProvider')
    return false
  }

  const { user, permissions } = authContext

  if (!user || !permissions) {
    return false
  }

  if (user.ruolo === 'ADMIN') {
    return true
  }

  return permissionList.every((p) => permissions.includes(p))
}

/**
 * Custom hook to get the current user's role
 *
 * @returns string - User role (e.g., 'ADMIN', 'GM', 'CMM') or null
 *
 * @example
 * const userRole = useUserRole()
 * if (userRole === 'ADMIN') {
 *   // Show admin-only UI
 * }
 */
export const useUserRole = (): string | null => {
  const authContext = useContext(AuthContext)

  if (!authContext) {
    console.warn('useUserRole must be used within AuthProvider')
    return null
  }

  return authContext.user?.ruolo || null
}

/**
 * Custom hook to check if the current user is admin
 *
 * @returns boolean - true if user is admin, false otherwise
 *
 * @example
 * const isAdmin = useIsAdmin()
 * return (
 *   <>
 *     {isAdmin && <AdminPanel />}
 *   </>
 * )
 */
export const useIsAdmin = (): boolean => {
  const role = useUserRole()
  return role === 'ADMIN'
}

/**
 * Custom hook to check if the current user is a manager
 * Managers: ADMIN, GENERAL_MANAGER, GM_ASSISTANT, CMM, CBM
 *
 * @returns boolean - true if user is manager, false otherwise
 */
export const useIsManager = (): boolean => {
  const role = useUserRole()
  const managerRoles = ['ADMIN', 'GENERAL_MANAGER', 'GM_ASSISTANT', 'CMM', 'CBM']
  return role ? managerRoles.includes(role) : false
}

/**
 * Custom hook to get all user permissions
 *
 * @returns string[] - Array of permission codes
 *
 * @example
 * const perms = usePermissions()
 * console.log('User can:', perms)
 */
export const usePermissions = (): string[] => {
  const authContext = useContext(AuthContext)

  if (!authContext) {
    console.warn('usePermissions must be used within AuthProvider')
    return []
  }

  return authContext.permissions || []
}
