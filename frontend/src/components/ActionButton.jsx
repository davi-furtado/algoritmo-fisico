export function ActionButton({
  children,
  onClick,
  secondary = false,
  disabled = false
}) {
  return (
    <button
      type="button"
      className={`action-button${secondary ? ' secondary' : ''}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  )
}
