export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
export const APP_NAME = import.meta.env.VITE_APP_NAME || 'Garage Management System'
export const APP_VERSION = import.meta.env.VITE_APP_VERSION || '1.0.0'

// Token storage key
export const TOKEN_KEY = 'garage_access_token'

// API endpoints
export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  REFRESH: '/auth/refresh',
  LOGOUT: '/auth/logout',
  ME: '/auth/me',
  
  // Users
  USERS: '/users/',
  USERS_ME: '/users/me',
  
  // Customers
  CUSTOMERS: '/customers',
  CUSTOMER_DETAILS: (id: number) => `/customers/${id}/details`,
  CUSTOMER_STATS: (id: number) => `/customers/${id}/stats`,
  
  // Vehicles
  VEHICLES: '/vehicles',
  VEHICLE_HISTORY: (id: number) => `/vehicles/${id}/history`,
  VEHICLE_MAINTENANCE: (id: number) => `/vehicles/${id}/maintenance-status`,
  
  // Work Orders
  WORK_ORDERS: '/work-orders',
  WORK_ORDERS_NEXT_NUMERO: '/work-orders/next-numero-scheda',
  WORK_ORDER_STATUS: (id: number) => `/work-orders/${id}/status`,
  WORK_ORDERS_STATS: '/work-orders/stats',
  WORK_ORDERS_CALENDAR: '/work-orders/calendar',
  
  // Parts
  PARTS: '/parts',
  PARTS_INVENTORY: '/parts/inventory',
  PARTS_STOCK: (id: number) => `/parts/${id}/stock`,
  PARTS_CATEGORIES: '/parts/categories/list',
  PARTS_SUPPLIERS: '/parts/suppliers/list',
  
  // Tires
  TIRES: '/tires',
  TIRES_VEHICLE: (vehicleId: number) => `/tires/vehicle/${vehicleId}`,
  TIRES_ROTATION: '/tires/rotation',
  TIRES_ALERTS: '/tires/alerts/replacement-needed',
  TIRES_STATS: '/tires/stats/summary',
  
  // Courtesy Cars
  COURTESY_CARS: '/courtesy-cars',
  COURTESY_CARS_AVAILABLE: '/courtesy-cars/available',
  COURTESY_CAR_LOAN: (id: number) => `/courtesy-cars/${id}/loan`,
  COURTESY_CAR_RETURN: (id: number) => `/courtesy-cars/${id}/return`,
  COURTESY_CAR_MAINTENANCE: (id: number) => `/courtesy-cars/${id}/maintenance`,
  COURTESY_CARS_STATS: '/courtesy-cars/stats/summary',
  
  // Maintenance Schedules
  MAINTENANCE: '/maintenance-schedules',
  MAINTENANCE_SCHEDULES: '/maintenance-schedules',
  MAINTENANCE_ALERTS: '/maintenance-schedules/alerts',
  MAINTENANCE_VEHICLE: (vehicleId: number) => `/maintenance-schedules/vehicle/${vehicleId}`,
  MAINTENANCE_COMPLETE: (id: number) => `/maintenance-schedules/${id}/complete`,
  MAINTENANCE_SKIP: (id: number) => `/maintenance-schedules/${id}/skip`,
  MAINTENANCE_STATS: '/maintenance-schedules/stats/summary',
  
  // Notifications
  NOTIFICATIONS: '/notifications',
  NOTIFICATIONS_BULK: '/notifications/bulk',
  NOTIFICATIONS_MARK_READ: '/notifications/mark-read',
  NOTIFICATIONS_READ: (id: number) => `/notifications/${id}/read`,
  NOTIFICATIONS_UNREAD_COUNT: '/notifications/me/unread-count',
  NOTIFICATIONS_STATS: '/notifications/stats/summary',
  
  // Calendar Events
  CALENDAR_EVENTS: '/calendar-events',
  CALENDAR_EVENTS_VIEW: '/calendar-events/view',
  CALENDAR_EVENT_STATUS: (id: number) => `/calendar-events/${id}/status`,
  CALENDAR_EVENTS_SYNC: '/calendar-events/sync',
  CALENDAR_EVENTS_STATS: '/calendar-events/stats/summary',
  
  // Documents
  DOCUMENTS: '/documents',
  DOCUMENT_UPLOAD: (id: number) => `/documents/${id}/upload`,
  DOCUMENT_DOWNLOAD: (id: number) => `/documents/${id}/download`,
  DOCUMENTS_ENTITY: (entityType: string, entityId: number) => `/documents/entity/${entityType}/${entityId}`,
  DOCUMENTS_STATS: '/documents/stats/summary',
  
  // Activity Logs
  ACTIVITY_LOGS: '/activity-logs',
  ACTIVITY_LOGS_AUDIT: (entityType: string, entityId: number) => `/activity-logs/audit/${entityType}/${entityId}`,
  ACTIVITY_LOGS_USER: (userId: number) => `/activity-logs/user/${userId}/history`,
  ACTIVITY_LOGS_RECENT: '/activity-logs/recent/all',
  ACTIVITY_LOGS_STATS: '/activity-logs/stats/summary',
  ACTIVITY_LOGS_USER_ACTIVITY: '/activity-logs/stats/user-activity',
  
  // Dashboard
  DASHBOARD_SUMMARY: '/dashboard/summary',
  DASHBOARD_ALERTS: '/dashboard/alerts',
  DASHBOARD_RECENT_ACTIVITY: '/dashboard/recent-activity',
  DASHBOARD_STATS: '/dashboard/stats/overview',
  
  // System Tables
  SYSTEM_DAMAGE_TYPES: '/system-tables/damage-types',
  SYSTEM_CUSTOMER_TYPES: '/system-tables/customer-types',
  SYSTEM_WORKORDER_STATUS_TYPES: '/system-tables/work-order-status-types',
  SYSTEM_PRIORITY_TYPES: '/system-tables/priority-types',
}
