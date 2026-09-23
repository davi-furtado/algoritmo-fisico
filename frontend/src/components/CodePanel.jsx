export function CodePanel({ title, value, error = false, onCopy }) {
  return (
    <section className={`panel${error ? ' error' : ''}`}>
      <header className="panel-header">
        <h2>{title}</h2>
        <button
          type="button"
          className="icon-button"
          onClick={onCopy}
          disabled={!value}
          title={`Copiar ${title.toLowerCase()}`}
          aria-label={`Copiar ${title.toLowerCase()}`}
        >
          <MdContentCopy aria-hidden="true" focusable="false" />
        </button>
      </header>
      <pre className="code-content">
        {value || 'Nenhum resultado para exibir.'}
      </pre>
    </section>
  )
}