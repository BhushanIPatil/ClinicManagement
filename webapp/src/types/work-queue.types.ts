/**
 * Work Queue / Priority Queue Types
 */

export interface WorkQueueItem {
  id: string
  title: string
  description: string
  priority: Priority
  status: WorkQueueStatus
  entity_type: EntityType
  entity_id?: string | null
  assigned_to_user_id?: string | null
  assigned_to_user_name?: string | null
  due_date?: string | null
  completed_at?: string | null
  metadata?: Record<string, any>
  created_at?: string
  updated_at?: string
}

export type Priority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'

export type WorkQueueStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'

export type EntityType =
  | 'APPOINTMENT'
  | 'PATIENT'
  | 'INVOICE'
  | 'EMERGENCY'
  | 'ALERT'
  | 'APPROVAL'
  | 'TASK'

export interface WorkQueueCreateRequest {
  title: string
  description: string
  priority?: Priority
  entity_type: EntityType
  entity_id?: string
  assigned_to_user_id?: string
  due_date?: string
  metadata?: Record<string, any>
}

export interface WorkQueueUpdateRequest {
  title?: string
  description?: string
  priority?: Priority
  status?: WorkQueueStatus
  assigned_to_user_id?: string
  due_date?: string
  metadata?: Record<string, any>
}

export interface AssignWorkQueueRequest {
  assigned_to_user_id: string
}

export interface CompleteWorkQueueRequest {
  notes?: string
}
