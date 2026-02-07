/**
 * useMyTasks – load and mutate current user's personal tasks.
 */

import { useState, useEffect, useCallback } from 'react'
import { myTasksService } from '@/services/my-tasks.service'
import type { UserTask, CreateMyTaskRequest, UpdateMyTaskRequest } from '@/types/my-tasks.types'

export function useMyTasks(options?: { status?: string }) {
  const [items, setItems] = useState<UserTask[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchTasks = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await myTasksService.list({ limit: 100, status: options?.status })
      setItems(res.items)
      setTotal(res.total)
    } catch (err: unknown) {
      const msg = (err as { detail?: string })?.detail ?? (err as Error)?.message ?? 'Failed to load tasks'
      setError(String(msg))
      setItems([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [options?.status])

  useEffect(() => {
    fetchTasks()
  }, [fetchTasks])

  const createTask = useCallback(async (data: CreateMyTaskRequest): Promise<UserTask> => {
    const task = await myTasksService.create(data)
    setItems((prev) => [task, ...prev])
    setTotal((t) => t + 1)
    return task
  }, [])

  const updateTask = useCallback(async (id: string, data: UpdateMyTaskRequest): Promise<UserTask> => {
    const task = await myTasksService.update(id, data)
    setItems((prev) => prev.map((t) => (t.id === id ? task : t)))
    return task
  }, [])

  const deleteTask = useCallback(async (id: string): Promise<void> => {
    await myTasksService.delete(id)
    setItems((prev) => prev.filter((t) => t.id !== id))
    setTotal((t) => Math.max(0, t - 1))
  }, [])

  const completeTask = useCallback(async (id: string): Promise<UserTask> => {
    const task = await myTasksService.complete(id)
    setItems((prev) => prev.map((t) => (t.id === id ? task : t)))
    return task
  }, [])

  return {
    items,
    total,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    completeTask,
  }
}
