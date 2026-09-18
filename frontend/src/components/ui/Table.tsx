import type { ReactNode, TableHTMLAttributes } from "react";

interface TableProps extends TableHTMLAttributes<HTMLTableElement> {
  children: ReactNode;
}

export default function Table({ children, className = "", ...props }: TableProps) {
  return (
    <div className="overflow-x-auto rounded-md border border-line bg-surface">
      <table className={`min-w-full divide-y divide-line text-left text-sm ${className}`} {...props}>
        {children}
      </table>
    </div>
  );
}
