import { MdContentCopy } from 'react-icons/md'

export function CodePanel({
  title = 'Resultado',
  value = '',
  error = false,
  onCopy,
  className = '',
  ...props
}) {
  const panelClassName = ['panel', error ? 'error' : '', className]
    .filter(Boolean)
    .join(' ')

  const handleCopy = () => {
    if (!value) return
    onCopy?.()
  }

  return (
    <section className={panelClassName} {...props}>
      <header className="panel-header">
        <h2>{title}</h2>
        <button
          type="button"
          className="icon-button"
          onClick={handleCopy}
          disabled={!value}
          title={`Copiar ${title.toLowerCase()}`}
          aria-label={`Copiar ${title.toLowerCase()}`}
        >
          <MdContentCopy aria-hidden="true" focusable="false" />
        </button>
      </header>
      <pre className="code-content" aria-live={error ? 'assertive' : 'polite'}>
        {value || 'Nenhum resultado para exibir.'}
      </pre>
    </section>
  )
}
