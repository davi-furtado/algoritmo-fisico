import { useMemo, useRef, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/'

function ActionButton({
  children,
  onClick,
  secondary = false,
  disabled = false
}) {
  return (
    <button
      className={`action-button${secondary ? ' secondary' : ''}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  )
}

function CodePanel({ title, value, error = false, onCopy }) {
  return (
    <section className={`panel${error ? ' error' : ''}`}>
      <header className='panel-header'>
        <h2>{title}</h2>
        <button
          className='icon-button'
          onClick={onCopy}
          disabled={!value}
          title={`Copiar ${title.toLowerCase()}`}
        >
          ⧉
        </button>
      </header>
      <pre className='code-content'>
        {value || 'Nenhum resultado para exibir.'}
      </pre>
    </section>
  )
}

export default function App() {
  const inputRef = useRef(null)
  const [image, setImage] = useState(null)
  const [result, setResult] = useState(null)
  const [view, setView] = useState('pseudo')
  const [loading, setLoading] = useState(false)
  const [zoom, setZoom] = useState(false)
  const [message, setMessage] = useState('')

  const code = useMemo(
    () => (view === 'pseudo' ? result?.pseudocode : result?.python) || '',
    [result, view]
  )

  async function processImage(file) {
    if (!file) return
    setImage(URL.createObjectURL(file))
    setResult(null)
    setMessage('')
    setLoading(true)

    const form = new FormData()
    form.append('file', file)

    try {
      const response = await fetch(API_URL, { method: 'POST', body: form })
      const data = await response.json()
      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : JSON.stringify(data.detail || data)
        )
      }
      setResult(data)
      setView('pseudo')
    } catch (error) {
      setResult({
        error: `Erro ao conectar com o servidor: ${error.message}`,
        output: '',
        pseudocode: '',
        python: ''
      })
    } finally {
      setLoading(false)
    }
  }

  function chooseImage(event) {
    processImage(event.target.files?.[0])
    event.target.value = ''
  }

  async function copyText(value) {
    if (!value) return
    await navigator.clipboard.writeText(value)
    setMessage('Copiado para a área de transferência.')
    window.setTimeout(() => setMessage(''), 1800)
  }

  return (
    <main className='app-shell'>
      <div className='app-card'>
        <header className='app-header'>
          <div>
            <p className='eyebrow'>LEITOR DE ALGORITMOS FÍSICOS</p>
            <h1>Algoritmo Físico</h1>
            <p>
              Fotografe o algoritmo montado com os blocos e transforme-o em
              Python.
            </p>
          </div>
          <span className='status-dot' aria-label='Aplicação pronta' />
        </header>

        <input
          ref={inputRef}
          type='file'
          accept='image/jpeg,image/png,image/bmp,image/webp'
          hidden
          onChange={chooseImage}
        />
        <ActionButton onClick={() => inputRef.current?.click()}>
          ＋ Selecionar foto
        </ActionButton>

        {image && (
          <button className='preview-button' onClick={() => setZoom(true)}>
            <img src={image} alt='Pré-visualização do algoritmo' />
            <span>Clique para ampliar</span>
          </button>
        )}

        {loading && (
          <div className='loading'>
            <span className='spinner' /> Lendo os blocos...
          </div>
        )}

        {result?.output || result?.error ? (
          <CodePanel
            title={result.error ? 'Erro' : 'Saída'}
            value={
              result.error
                ? `${result.output ? `${result.output}\n\n` : ''}${result.error}`
                : result.output
            }
            error={Boolean(result.error)}
            onCopy={() => copyText(result.error || result.output)}
          />
        ) : null}

        {(result?.pseudocode || result?.python) && (
          <section className='panel code-panel'>
            <div className='code-toolbar'>
              <div
                className='toggle'
                role='tablist'
                aria-label='Linguagem do código'
              >
                <button
                  className={view === 'pseudo' ? 'active' : ''}
                  onClick={() => setView('pseudo')}
                >
                  Pseudocódigo
                </button>
                <button
                  className={view === 'python' ? 'active' : ''}
                  onClick={() => setView('python')}
                >
                  Python
                </button>
              </div>
              <button
                className='icon-button'
                onClick={() => copyText(code)}
                disabled={!code}
                title='Copiar código'
              >
                ⧉
              </button>
            </div>
            <pre className='code-content'>{code}</pre>
          </section>
        )}

        {message && <p className='toast'>{message}</p>}
      </div>

      {zoom && (
        <div
          className='modal-backdrop'
          role='dialog'
          aria-modal='true'
          onClick={() => setZoom(false)}
        >
          <img
            src={image}
            alt='Algoritmo ampliado'
            onClick={event => event.stopPropagation()}
          />
          <button className='close-button' onClick={() => setZoom(false)}>
            Fechar
          </button>
        </div>
      )}
    </main>
  )
}

