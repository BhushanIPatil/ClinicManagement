import { WorkQueueList } from '@/components/features/WorkQueueList'

export default function WorkQueuePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Work Queue</h1>
      <WorkQueueList />
    </div>
  )
}
