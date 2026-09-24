export function ActionButton({
  children,
  onClick,
  secondary = false,
  disabled = false,
  className = '',
  ...props
}) {
  const handleClick = (event) => {
    if (disabled) return
    onClick?.(event)
  }

  const combinedClassName = [
    'action-button',
    secondary ? 'secondary' : '',
    className
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <button
      type="button"
      className={combinedClassName}
      onClick={handleClick}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  )
}
