import { Link } from "react-router-dom";

export default function SpectralAction({
  to,
  children,
  className = "",
  variant = "default",
  onClick,
  type = "button",
  ariaLabel
}) {
  const cls = `spectralAction spectralAction--${variant} ${className}`.trim();

  if (to) {
    return (
      <Link className={cls} to={to} aria-label={ariaLabel}>
        <span className="spectralAction__inner">{children}</span>
      </Link>
    );
  }

  return (
    <button className={cls} type={type} onClick={onClick} aria-label={ariaLabel}>
      <span className="spectralAction__inner">{children}</span>
    </button>
  );
}
