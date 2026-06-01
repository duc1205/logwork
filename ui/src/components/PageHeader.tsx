import type { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  subtitle?: ReactNode;
  aside?: ReactNode;
  children?: ReactNode;
}

export function PageHeader({ title, subtitle, aside, children }: PageHeaderProps) {
  return (
    <header className="page-header">
      <div>
        <h1>{title}</h1>
        {subtitle && <p className="muted page-subtitle">{subtitle}</p>}
        {children}
      </div>
      {aside}
    </header>
  );
}
