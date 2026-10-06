import type { HTMLAttributes } from "react";

interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  className?: string;
}

export default function Skeleton({ className = "", ...props }: SkeletonProps) {
  return (
    <div
      className={`animate-pulse rounded-sm bg-line/60 dark:bg-farmer-800/60 ${className}`}
      aria-hidden="true"
      {...props}
    />
  );
}
