/**
 * useWorkQueue Hook
 * 
 * Hook for managing work queue items with loading and error states.
 */

import { useState, useEffect, useCallback } from 'react'
import { workQueueService } from '@/services/work-queue.service'
import type {
  WorkQueueItem,
  WorkQueueCreateRequest,
  WorkQueueUpdateRequest,
  AssignWorkQueueRequest,
} from '@/types/work-queue.types'

interface UseWorkQueueOptions {
  autoFetch?: boolean
  status?: string
  priority?: string
  /** Only future items (due_date >= now, not completed/cancelled) */
  future_only?: boolean
}

export function useWorkQueue(options: UseWorkQueueOptions = {}) {
  const { autoFetch = true, status, priority, future_only } = options

  const [items, setItems] = useState<WorkQueueItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchItems = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await workQueueService.listItems({ status, priority, future_only })
      setItems(data)
    } catch (err: any) {
      setError(err?.detail || 'Failed to fetch work queue items')
    } finally {
      setLoading(false)
    }
  }, [status, priority, future_only])

  const fetchVisibleItems = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await workQueueService.getVisibleItems()
      setItems(data)
    } catch (err: any) {
      setError(err?.detail || 'Failed to fetch visible items')
    } finally {
      setLoading(false)
    }
  }, [])

  const createItem = useCallback(async (data: WorkQueueCreateRequest) => {
    setLoading(true)
    setError(null)
    try {
      const item = await workQueueService.createItem(data)
      setItems((prev) => [item, ...prev])
      return item
    } catch (err: any) {
      setError(err?.detail || 'Failed to create work queue item')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const updateItem = useCallback(
    async (id: string, data: WorkQueueUpdateRequest) => {
      setLoading(true)
      setError(null)
      try {
        const item = await workQueueService.updateItem(id, data)
        setItems((prev) => prev.map((i) => (i.id === id ? item : i)))
        return item
      } catch (err: any) {
        setError(err?.detail || 'Failed to update item')
        throw err
      } finally {
        setLoading(false)
      }
    },
    []
  )

  const assignItem = useCallback(
    async (id: string, data: AssignWorkQueueRequest) => {
      setLoading(true)
      setError(null)
      try {
        const item = await workQueueService.assignItem(id, data)
        setItems((prev) => prev.map((i) => (i.id === id ? item : i)))
        return item
      } catch (err: any) {
        setError(err?.detail || 'Failed to assign item')
        throw err
      } finally {
        setLoading(false)
      }
    },
    []
  )

  const completeItem = useCallback(async (id: string) => {
    setLoading(true)
    setError(null)
    try {
      const item = await workQueueService.completeItem(id)
      setItems((prev) => prev.map((i) => (i.id === id ? item : i)))
      return item
    } catch (err: any) {
      setError(err?.detail || 'Failed to complete item')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (autoFetch) {
      fetchItems()
    }
  }, [fetchItems, autoFetch])

  return {
    items,
    loading,
    error,
    fetchItems,
    fetchVisibleItems,
    createItem,
    updateItem,
    assignItem,
    completeItem,
  }
}
