/**
 * My Tasks Service – personal tasks (scoped by current user).
 */

import { apiService } from './api.service'
import type { UserTask, CreateMyTaskRequest, UpdateMyTaskRequest } from '@/types/my-tasks.types'

class MyTasksService {
  async list(params?: { skip?: number; limit?: number; status?: string }): Promise<{ items: UserTask[]; total: number }> {
    const q = new URLSearchParams()
    if (params?.skip != null) q.set('skip', String(params.skip))
    if (params?.limit != null) q.set('limit', String(params.limit))
    if (params?.status) q.set('status', params.status)
    const res = await apiService.get<{ items?: UserTask[]; total?: number }>(`/my-tasks?${q}`)
    return { items: Array.isArray(res?.items) ? res.items : [], total: res?.total ?? 0 }
  }

  async get(id: string): Promise<UserTask> {
    return apiService.get<UserTask>(`/my-tasks/${id}`)
  }

  async create(data: CreateMyTaskRequest): Promise<UserTask> {
    return apiService.post<UserTask>('/my-tasks', data)
  }

  async update(id: string, data: UpdateMyTaskRequest): Promise<UserTask> {
    return apiService.put<UserTask>(`/my-tasks/${id}`, data)
  }

  async delete(id: string): Promise<{ deleted: boolean }> {
    return apiService.delete<{ deleted: boolean }>(`/my-tasks/${id}`)
  }

  async complete(id: string): Promise<UserTask> {
    return apiService.post<UserTask>(`/my-tasks/${id}/complete`)
  }
}

export const myTasksService = new MyTasksService()
