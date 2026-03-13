interface PageHeaderProps {
  title: string;
  subtitle: string;
  children?: React.ReactNode;
}

export function PageHeader({ title, subtitle, children }: PageHeaderProps) {
  return (
    <div className="flex items-start justify-between mb-6 animate-fade-in-up">
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">
          {title}
        </h1>
        <p className="text-sm text-gray-400 mt-0.5">{subtitle}</p>
      </div>
      {children && <div className="flex items-center gap-2">{children}</div>}
    </div>
  );
}
