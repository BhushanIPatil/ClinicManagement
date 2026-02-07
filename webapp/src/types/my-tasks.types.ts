/** My Tasks – personal tasks per user, not visible to others. */

export interface UserTask {
  id: string
  title: string
  description: string | null
  status: UserTaskStatus
  priority: string
  due_date: string | null
  completed_at: string | null
  created_at?: string
  updated_at?: string
}

export type UserTaskStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'

export interface CreateMyTaskRequest {
  title: string
  description?: string
  priority?: string
  due_date?: string
}

export interface UpdateMyTaskRequest {
  title?: string
  description?: string
  priority?: string
  due_date?: string
  status?: UserTaskStatus
}
