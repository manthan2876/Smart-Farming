import type { SVGProps } from "react";

export interface IconProps extends SVGProps<SVGSVGElement> {
  size?: number | string;
  className?: string;
}

const baseProps = (size: number | string = 18, className = "") => ({
  width: size,
  height: size,
  viewBox: "0 0 20 20",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.5,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  className,
  "aria-hidden": "true" as const,
});

export function Sprout({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M10 18v-7" />
      <path d="M10 11a5 5 0 0 1-7-4 5 5 0 0 1 7 0" />
      <path d="M10 14a5 5 0 0 0 7-4 5 5 0 0 0-7 0" />
    </svg>
  );
}

export function Leaf({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M3 17c0-7 5-13 14-14 0 9-6 14-14 14z" />
      <path d="M3 17l9-9" />
    </svg>
  );
}

export function Scan({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M3 7V4a1 1 0 0 1 1-1h3" />
      <path d="M13 3h3a1 1 0 0 1 1 1v3" />
      <path d="M17 13v3a1 1 0 0 1-1 1h-3" />
      <path d="M7 17H4a1 1 0 0 1-1-1v-3" />
      <line x1="3" y1="10" x2="17" y2="10" />
    </svg>
  );
}

export function ScanSearch({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M3 6V4a1 1 0 0 1 1-1h2" />
      <path d="M14 3h2a1 1 0 0 1 1 1v2" />
      <path d="M17 14v2a1 1 0 0 1-1 1h-2" />
      <path d="M6 17H4a1 1 0 0 1-1-1v-2" />
      <circle cx="10" cy="10" r="3" />
      <path d="m12.5 12.5 2.5 2.5" />
    </svg>
  );
}

export function History({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <circle cx="10" cy="10" r="7" />
      <polyline points="10 6 10 10 13 12" />
      <path d="M10 3a7 7 0 0 0-6 3.5L3 5" />
    </svg>
  );
}

export function LayoutDashboard({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <rect x="3" y="3" width="6" height="6" rx="0.5" />
      <rect x="11" y="3" width="6" height="4" rx="0.5" />
      <rect x="11" y="9" width="6" height="8" rx="0.5" />
      <rect x="3" y="11" width="6" height="6" rx="0.5" />
    </svg>
  );
}

export function MapPin({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M10 18s-5.5-5.5-5.5-9a5.5 5.5 0 0 1 11 0c0 3.5-5.5 9-5.5 9z" />
      <circle cx="10" cy="9" r="2" />
    </svg>
  );
}

export function Map({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <polygon points="3 5 7 3 13 6 17 4 17 15 13 17 7 14 3 16 3 5" />
      <line x1="7" y1="3" x2="7" y2="14" />
      <line x1="13" y1="6" x2="13" y2="17" />
    </svg>
  );
}

export function Settings({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <circle cx="10" cy="10" r="3" />
      <path d="M16.5 10a6.5 6.5 0 0 0-.2-1.5l1.4-.8-1.5-2.6-1.5.7a6.5 6.5 0 0 0-2.4-1.4l-.3-1.6h-3l-.3 1.6A6.5 6.5 0 0 0 6.3 5.8l-1.5-.7-1.5 2.6 1.4.8A6.5 6.5 0 0 0 4.5 10a6.5 6.5 0 0 0 .2 1.5l-1.4.8 1.5 2.6 1.5-.7a6.5 6.5 0 0 0 2.4 1.4l.3 1.6h3l.3-1.6a6.5 6.5 0 0 0 2.4-1.4l1.5.7 1.5-2.6-1.4-.8a6.5 6.5 0 0 0 .2-1.5z" />
    </svg>
  );
}

export function CloudSun({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M9.5 7a3 3 0 1 1 5 2.6" />
      <path d="M5.5 16h8a3.5 3.5 0 0 0 0-7 4 4 0 0 0-7.8 1.2A2.7 2.7 0 0 0 5.5 16z" />
    </svg>
  );
}

export function Cloud({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M5 15h9.5a3.5 3.5 0 0 0 0-7 4 4 0 0 0-7.5.8A3 3 0 0 0 5 15z" />
    </svg>
  );
}

export function Bell({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M15 14H5c.8-1 1.5-2.2 1.5-5a3.5 3.5 0 0 1 7 0c0 2.8.7 4 1.5 5z" />
      <path d="M8.5 16a1.5 1.5 0 0 0 3 0" />
    </svg>
  );
}

export function ShieldAlert({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M10 2s6 2.5 6 7c0 4.5-4 8-6 9-2-1-6-4.5-6-9 0-4.5 6-7 6-7z" />
      <line x1="10" y1="7" x2="10" y2="10" />
      <circle cx="10" cy="13" r="0.6" fill="currentColor" />
    </svg>
  );
}

export function ShieldCheck({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M10 2s6 2.5 6 7c0 4.5-4 8-6 9-2-1-6-4.5-6-9 0-4.5 6-7 6-7z" />
      <polyline points="7.5 9.5 9 11 12.5 7.5" />
    </svg>
  );
}

export function Shield({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M10 2s6 2.5 6 7c0 4.5-4 8-6 9-2-1-6-4.5-6-9 0-4.5 6-7 6-7z" />
    </svg>
  );
}

export function Users({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M13.5 16.5v-1a3 3 0 0 0-3-3h-3a3 3 0 0 0-3 3v1" />
      <circle cx="7.5" cy="6.5" r="2.5" />
      <path d="M16.5 16.5v-1a2.5 2.5 0 0 0-2-2.4" />
      <path d="M12.5 4.2a2.5 2.5 0 0 1 0 4.6" />
    </svg>
  );
}

export function User({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M16 16.5v-1.5a3.5 3.5 0 0 0-3.5-3.5h-5A3.5 3.5 0 0 0 4 15v1.5" />
      <circle cx="10" cy="6.5" r="3" />
    </svg>
  );
}

export function UserPlus({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M13 16.5v-1.5a3.5 3.5 0 0 0-3.5-3.5h-5A3.5 3.5 0 0 0 1 15v1.5" />
      <circle cx="7" cy="6.5" r="3" />
      <line x1="16" y1="8" x2="16" y2="12" />
      <line x1="14" y1="10" x2="18" y2="10" />
    </svg>
  );
}

export function UserCheck({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M13 16.5v-1.5a3.5 3.5 0 0 0-3.5-3.5h-5A3.5 3.5 0 0 0 1 15v1.5" />
      <circle cx="7" cy="6.5" r="3" />
      <polyline points="14 9.5 15.5 11 18.5 8" />
    </svg>
  );
}

export function FileText({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M12 2H5a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V6l-4-4z" />
      <polyline points="12 2 12 6 16 6" />
      <line x1="7" y1="10" x2="13" y2="10" />
      <line x1="7" y1="13" x2="11" y2="13" />
    </svg>
  );
}

export function ClipboardList({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <rect x="4" y="4" width="12" height="13" rx="1" />
      <path d="M7 4V3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1" />
      <line x1="7" y1="8" x2="13" y2="8" />
      <line x1="7" y1="11" x2="13" y2="11" />
      <line x1="7" y1="14" x2="10" y2="14" />
    </svg>
  );
}

export function LogOut({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M7 16H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h3" />
      <polyline points="12 13 16 10 12 7" />
      <line x1="16" y1="10" x2="6" y2="10" />
    </svg>
  );
}

export function LogIn({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M12 4h4a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1h-4" />
      <polyline points="8 7 12 10 8 13" />
      <line x1="12" y1="10" x2="3" y2="10" />
    </svg>
  );
}

export function Menu({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <line x1="3" y1="5" x2="17" y2="5" />
      <line x1="3" y1="10" x2="17" y2="10" />
      <line x1="3" y1="15" x2="17" y2="15" />
    </svg>
  );
}

export function X({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <line x1="4" y1="4" x2="16" y2="16" />
      <line x1="16" y1="4" x2="4" y2="16" />
    </svg>
  );
}

export function Check({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <polyline points="4 10.5 8 14.5 16 5.5" />
    </svg>
  );
}

export function CheckCircle({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <circle cx="10" cy="10" r="7" />
      <polyline points="6.5 10 8.5 12 13.5 7.5" />
    </svg>
  );
}

export function CheckCircle2({ size = 18, className = "", ...props }: IconProps) {
  return <CheckCircle size={size} className={className} {...props} />;
}

export function XCircle({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <circle cx="10" cy="10" r="7" />
      <line x1="7.5" y1="7.5" x2="12.5" y2="12.5" />
      <line x1="12.5" y1="7.5" x2="7.5" y2="12.5" />
    </svg>
  );
}

export function AlertCircle({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <circle cx="10" cy="10" r="7" />
      <line x1="10" y1="6.5" x2="10" y2="10.5" />
      <circle cx="10" cy="13.2" r="0.6" fill="currentColor" />
    </svg>
  );
}

export function AlertTriangle({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M9.13 3.5a1 1 0 0 1 1.74 0l6.5 11.5A1 1 0 0 1 16.5 16.5H3.5a1 1 0 0 1-.87-1.5l6.5-11.5z" />
      <line x1="10" y1="8" x2="10" y2="11.5" />
      <circle cx="10" cy="14" r="0.6" fill="currentColor" />
    </svg>
  );
}

export function Info({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <circle cx="10" cy="10" r="7" />
      <line x1="10" y1="9.5" x2="10" y2="13.5" />
      <circle cx="10" cy="6.8" r="0.6" fill="currentColor" />
    </svg>
  );
}

export function ChevronDown({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <polyline points="5 7.5 10 12.5 15 7.5" />
    </svg>
  );
}

export function ChevronRight({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <polyline points="7.5 5 12.5 10 7.5 15" />
    </svg>
  );
}

export function ArrowRight({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <line x1="3" y1="10" x2="16" y2="10" />
      <polyline points="11 5 16 10 11 15" />
    </svg>
  );
}

export function ArrowLeft({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <line x1="17" y1="10" x2="4" y2="10" />
      <polyline points="9 5 4 10 9 15" />
    </svg>
  );
}

export function Search({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <circle cx="8.5" cy="8.5" r="5" />
      <line x1="12.5" y1="12.5" x2="16.5" y2="16.5" />
    </svg>
  );
}

export function Filter({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <polygon points="3 4 17 4 11 11 11 16 9 14 9 11 3 4" />
    </svg>
  );
}

export function Eye({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M2 10s3-5.5 8-5.5 8 5.5 8 5.5-3 5.5-8 5.5-8-5.5-8-5.5z" />
      <circle cx="10" cy="10" r="2.5" />
    </svg>
  );
}

export function EyeOff({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M2 10s3-5.5 8-5.5 8 5.5 8 5.5-3 5.5-8 5.5-8-5.5-8-5.5z" />
      <circle cx="10" cy="10" r="2.5" />
      <line x1="3" y1="3" x2="17" y2="17" />
    </svg>
  );
}

export function Upload({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M15 13v3a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-3" />
      <polyline points="7 7 10 4 13 7" />
      <line x1="10" y1="4" x2="10" y2="13" />
    </svg>
  );
}

export function Camera({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M6.5 4h7l1.5 2H17a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h2z" />
      <circle cx="10" cy="11" r="3" />
    </svg>
  );
}

export function Globe({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <circle cx="10" cy="10" r="7" />
      <line x1="3" y1="10" x2="17" y2="10" />
      <ellipse cx="10" cy="10" rx="3.5" ry="7" />
    </svg>
  );
}

export function Loader2({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M10 3a7 7 0 0 1 7 7" />
    </svg>
  );
}

export function Activity({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <polyline points="3 10 6 10 8 4 12 16 14 10 17 10" />
    </svg>
  );
}

export function Droplet({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M10 3c-3.5 4-5 6.5-5 9a5 5 0 0 0 10 0c0-2.5-1.5-5-5-9z" />
    </svg>
  );
}

export function Bug({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <rect x="7" y="7" width="6" height="8" rx="3" />
      <path d="M8 5a2 2 0 0 1 4 0" />
      <line x1="4" y1="10" x2="7" y2="10" />
      <line x1="13" y1="10" x2="16" y2="10" />
      <line x1="4.5" y1="6.5" x2="7" y2="8" />
      <line x1="15.5" y1="6.5" x2="13" y2="8" />
      <line x1="4.5" y1="13.5" x2="7" y2="12" />
      <line x1="15.5" y1="13.5" x2="13" y2="12" />
    </svg>
  );
}

export function Cpu({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <rect x="6" y="6" width="8" height="8" rx="1" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="12" y1="2" x2="12" y2="6" />
      <line x1="8" y1="14" x2="8" y2="18" />
      <line x1="12" y1="14" x2="12" y2="18" />
      <line x1="2" y1="8" x2="6" y2="8" />
      <line x1="2" y1="12" x2="6" y2="12" />
      <line x1="14" y1="8" x2="18" y2="8" />
      <line x1="14" y1="12" x2="18" y2="12" />
    </svg>
  );
}

export function Sun({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <circle cx="10" cy="10" r="3.5" />
      <line x1="10" y1="2" x2="10" y2="4.5" />
      <line x1="10" y1="15.5" x2="10" y2="18" />
      <line x1="2" y1="10" x2="4.5" y2="10" />
      <line x1="15.5" y1="10" x2="18" y2="10" />
      <line x1="4.3" y1="4.3" x2="6" y2="6" />
      <line x1="14" y1="14" x2="15.7" y2="15.7" />
      <line x1="4.3" y1="15.7" x2="6" y2="14" />
      <line x1="14" y1="6" x2="15.7" y2="4.3" />
    </svg>
  );
}

export function Moon({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M15.5 12A6.5 6.5 0 0 1 8 4.5a6.5 6.5 0 1 0 7.5 7.5z" />
    </svg>
  );
}

export function Laptop({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <rect x="4" y="5" width="12" height="8" rx="0.5" />
      <line x1="2" y1="15" x2="18" y2="15" />
    </svg>
  );
}

export function Download({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M15 13v3a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-3" />
      <polyline points="7 9 10 12 13 9" />
      <line x1="10" y1="3" x2="10" y2="12" />
    </svg>
  );
}

export function Image({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <rect x="3" y="3" width="14" height="14" rx="1" />
      <circle cx="7.5" cy="7.5" r="1.5" />
      <polyline points="17 13 13 9 5 17" />
    </svg>
  );
}

export function Volume2({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <polygon points="4 7 8 7 12 4 12 16 8 13 4 13 4 7" />
      <path d="M15 7a4 4 0 0 1 0 6" />
      <path d="M17 5a6.5 6.5 0 0 1 0 10" />
    </svg>
  );
}

export function Pause({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <line x1="7" y1="5" x2="7" y2="15" />
      <line x1="13" y1="5" x2="13" y2="15" />
    </svg>
  );
}

export function Printer({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <polyline points="6 8 6 3 14 3 14 8" />
      <rect x="4" y="8" width="12" height="7" rx="1" />
      <path d="M6 14v3h8v-3" />
    </svg>
  );
}

export function Save({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M14 2H5a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V5l-2-3z" />
      <polyline points="14 2 14 6 7 6 7 2" />
      <rect x="7" y="11" width="6" height="5" />
    </svg>
  );
}

export function Trash2({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <polyline points="3 5 17 5" />
      <path d="M6 5v11a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V5" />
      <path d="M8 5V3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v2" />
    </svg>
  );
}

export function RotateCcw({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M3 4v4h4" />
      <path d="M3.5 12a7 7 0 1 0 1.8-5.3L3 8" />
    </svg>
  );
}

export const RefreshCw = RotateCcw;

export function Navigation2({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <polygon points="10 2 16 16 10 13 4 16 10 2" />
    </svg>
  );
}

export function Satellite({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M12 3l5 5-2 2-5-5 2-2z" />
      <path d="M8 7l5 5-2 2-5-5 2-2z" />
      <line x1="3" y1="17" x2="7" y2="13" />
    </svg>
  );
}

export function GraduationCap({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <polygon points="10 3 18 7 10 11 2 7 10 3" />
      <path d="M5 8.5v4.5c0 2 2.5 3.5 5 3.5s5-1.5 5-3.5V8.5" />
      <line x1="18" y1="7" x2="18" y2="13" />
    </svg>
  );
}

export function Mail({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <rect x="3" y="4" width="14" height="12" rx="1" />
      <polyline points="3 6 10 11 17 6" />
    </svg>
  );
}

export function Lock({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <rect x="4" y="9" width="12" height="9" rx="1" />
      <path d="M6 9V6a4 4 0 0 1 8 0v3" />
    </svg>
  );
}

export function KeyRound({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <circle cx="7" cy="10" r="4" />
      <path d="M11 10h6v3h-2v-3" />
    </svg>
  );
}

export function Wheat({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M10 18v-8" />
      <path d="M10 10c-1-1.5-1-3 0-4.5 1 1.5 1 3 0 4.5z" />
      <path d="M7 12c-1.5-.5-2-2-1.5-3.5 1.5 0 2.5 1 1.5 3.5z" />
      <path d="M13 12c1.5-.5 2-2 1.5-3.5-1.5 0-2.5 1-1.5 3.5z" />
    </svg>
  );
}

export function TreeDeciduous({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M10 18v-5" />
      <circle cx="10" cy="8" r="5.5" />
    </svg>
  );
}

export function Clover({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M10 18v-6" />
      <circle cx="7" cy="9" r="2.5" />
      <circle cx="13" cy="9" r="2.5" />
      <circle cx="10" cy="6" r="2.5" />
    </svg>
  );
}

export function Sliders({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <line x1="3" y1="5" x2="17" y2="5" />
      <line x1="3" y1="10" x2="17" y2="10" />
      <line x1="3" y1="15" x2="17" y2="15" />
      <circle cx="7" cy="5" r="1.5" fill="currentColor" />
      <circle cx="13" cy="10" r="1.5" fill="currentColor" />
      <circle cx="9" cy="15" r="1.5" fill="currentColor" />
    </svg>
  );
}

export function Database({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <ellipse cx="10" cy="5" rx="7" ry="2.5" />
      <path d="M3 5v5c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5V5" />
      <path d="M3 10v5c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5v-5" />
    </svg>
  );
}

export function FolderArchive({ size = 18, className = "", ...props }: IconProps) {
  return (
    <svg {...baseProps(size, className)} {...props}>
      <path d="M3 5a1 1 0 0 1 1-1h4l2 2h6a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5z" />
      <line x1="8" y1="11" x2="12" y2="11" />
    </svg>
  );
}

export const DownloadCloud = Download;
