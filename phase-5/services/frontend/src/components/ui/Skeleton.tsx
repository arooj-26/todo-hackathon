/**
 * Skeleton loading component
 */
export default function Skeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-pulse bg-gray-200 rounded ${className}`}></div>
  )
}

export function TaskItemSkeleton() {
  return (
    <div className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-lg">
      <Skeleton className="w-5 h-5 rounded" />
      <Skeleton className="flex-1 h-5" />
      <div className="flex gap-2">
        <Skeleton className="w-12 h-8 rounded" />
        <Skeleton className="w-12 h-8 rounded" />
        <Skeleton className="w-16 h-8 rounded" />
      </div>
    </div>
  )
}

export function TaskListSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, index) => (
        <TaskItemSkeleton key={index} />
      ))}
    </div>
  )
}
