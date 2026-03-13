import { cn } from "@/lib/utils";

export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "animate-shimmer rounded-2xl h-[120px] border border-gray-100",
        className
      )}
    />
  );
}

export function SkeletonRow() {
  return (
    <div className="animate-shimmer rounded-xl h-[56px] border border-gray-100 mb-1.5" />
  );
}

export function SkeletonChart({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "animate-shimmer rounded-2xl h-[320px] border border-gray-100",
        className
      )}
    />
  );
}
