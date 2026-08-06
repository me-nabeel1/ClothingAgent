interface StatusDotProps {
  status: "checking" | "online" | "offline";
  label: string;
}

export function StatusDot({ status, label }: StatusDotProps) {
  return (
    <span className={`status-dot status-dot--${status}`} title={`${label}: ${status}`}>
      <span aria-hidden="true" />
      {label}
    </span>
  );
}
