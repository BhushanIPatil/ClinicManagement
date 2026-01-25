/**
 * Work Queue Service
 * 
 * Handles all work queue/priority queue API calls.
 */

import { apiService } from './api.service'
import type {
  WorkQueueItem,
  WorkQueueCreateRequest,
  WorkQueueUpdateRequest,
  AssignWorkQueueRequest,
  CompleteWorkQueueRequest,
} from '@/types/work-queue.types'

class WorkQueueService {
  /**
   * Create work queue item
   */
  async createItem(data: WorkQueueCreateRequest): Promise<WorkQueueItem> {
    return apiService.post<WorkQueueItem>('/work-queue', data)
  }

  /**
   * Get work queue item by ID
   */
  async getItem(id: string): Promise<WorkQueueItem> {
    return apiService.get<WorkQueueItem>(`/work-queue/${id}`)
  }

  /**
   * List work queue items. API returns { items, total, skip, limit }; this returns items, or [] when missing.
   */
  async listItems(params?: {
    status?: string
    priority?: string
    entity_type?: string
    skip?: number
    limit?: number
  }): Promise<WorkQueueItem[]> {
    const queryParams = new URLSearchParams()
    if (params?.status) queryParams.append('status', params.status)
    if (params?.priority) queryParams.append('priority', params.priority)
    if (params?.entity_type) queryParams.append('entity_type', params.entity_type)
    if (params?.skip != null) queryParams.append('skip', String(params.skip))
    if (params?.limit != null) queryParams.append('limit', String(params.limit))

    const query = queryParams.toString()
    const res = await apiService.get<{ items?: WorkQueueItem[]; total?: number }>(
      `/work-queue${query ? `?${query}` : ''}`
    )
    return Array.isArray(res?.items) ? res.items : []
  }

  /**
   * Get visible items (role-based)
   */
  async getVisibleItems(): Promise<WorkQueueItem[]> {
    return apiService.get<WorkQueueItem[]>('/work-queue/visible')
  }

  /**
   * Get my assignments
   */
  async getMyAssignments(): Promise<WorkQueueItem[]> {
    return apiService.get<WorkQueueItem[]>('/work-queue/my-assignments')
  }

  /**
   * Update work queue item
   */
  async updateItem(
    id: string,
    data: WorkQueueUpdateRequest
  ): Promise<WorkQueueItem> {
    return apiService.put<WorkQueueItem>(`/work-queue/${id}`, data)
  }

  /**
   * Assign work queue item
   */
  async assignItem(
    id: string,
    data: AssignWorkQueueRequest
  ): Promise<WorkQueueItem> {
    return apiService.post<WorkQueueItem>(`/work-queue/${id}/assign`, data)
  }

  /**
   * Complete work queue item
   */
  async completeItem(
    id: string,
    data?: CompleteWorkQueueRequest
  ): Promise<WorkQueueItem> {
    return apiService.post<WorkQueueItem>(
      `/work-queue/${id}/complete`,
      data || {}
    )
  }

  /**
   * Cancel work queue item
   */
  async cancelItem(id: string): Promise<WorkQueueItem> {
    return apiService.post<WorkQueueItem>(`/work-queue/${id}/cancel`)
  }
}

export const workQueueService = new WorkQueueService()
