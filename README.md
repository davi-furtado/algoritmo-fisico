# Algoritmo Físico

O **Algoritmo Físico** reconhece algoritmos montados com blocos físicos
identificados por marcadores ArUco. A imagem é analisada, os blocos são
reconstruídos como pseudocódigo, o algoritmo é convertido para Python e sua
saída é exibida ao usuário.

O repositório contém três superfícies de uso:

- uma API HTTP em FastAPI;
- um site em React com Vite;
- uma interface desktop em CustomTkinter.

## Funcionalidades

- Detecção de marcadores ArUco em imagens JPG, JPEG, PNG, BMP e WEBP.
- Correção da orientação da foto e agrupamento proporcional dos blocos em
  linhas.
- Reconstrução e indentação do pseudocódigo.
- Conversão do pseudocódigo reconhecido para Python.
- Interpretação do algoritmo com limite de passos e limite de saída.
- Mensagens de erro em português para algoritmos incompletos ou inválidos.
- Upload de imagem pelo navegador, preview, visualização ampliada e cópia dos
  resultados.
- Seleção de uma imagem ou de uma pasta na interface desktop.
- Materiais PDF para impressão dos blocos e exercícios de lógica.

## Estrutura atual

A árvore foi revisada com `uv run pyletree -g`. O diretório `.git` e os
artefatos gerados (`node_modules`, `frontend/dist` e caches locais) não são
fontes do aplicativo e, por isso, estão omitidos da representação abaixo.

```text
algoritmo-fisico/
├── .gitignore
├── .python-version
├── LICENSE
├── README.md
├── pyproject.toml
├── uv.lock
├── api.py                         # API FastAPI e endpoint POST /
├── interface.py                   # Interface desktop CustomTkinter
├── blocks/
│   ├── blocks.json                # Mapeamento dos IDs ArUco
│   ├── blocks.pdf                 # Blocos físicos para impressão
│   ├── problems.pdf               # Exercícios de lógica
│   ├── generator.py               # Geração dos marcadores
│   └── arucos/                    # PNGs dos marcadores gerados
├── core/
│   ├── blocks.json                # Mapeamento usado pelo núcleo
│   ├── converter.py               # Limpeza e conversão para Python
│   ├── interpreter.py             # Interpretador seguro do pseudocódigo
│   ├── pipeline.py                # Entrada única do processamento
│   └── reader.py                  # Leitura e ordenação dos ArUco
├── frontend/
│   ├── .env
│   ├── .gitignore
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── public/
│   │   ├── favicon.svg
│   │   ├── icons.svg
│   │   └── JetBrainsMonoNL-Bold.ttf
│   └── src/
│       ├── App.jsx                # Interface web e integração com a API
│       ├── index.css              # Layout e tema visual
│       └── main.jsx               # Ponto de entrada React
├── pics/                          # Imagens de teste e exemplos
└── tests/
    ├── api.py                     # Testes da API
    ├── api_multiple.py            # Testes da API com várias imagens
    ├── core.py                    # Testes do núcleo
    ├── core_multiple.py           # Testes do núcleo com várias imagens
    └── results.json               # Resultados esperados ou registrados
```

## Requisitos

- Python 3.13 ou superior, conforme `.python-version` e `pyproject.toml`.
- [uv](https://docs.astral.sh/uv/) para instalar e executar o ambiente Python.
- Node.js e npm para o frontend.

As dependências Python incluem FastAPI, Uvicorn, OpenCV, NumPy, Pillow,
CustomTkinter, Requests, python-multipart e pyletree. As dependências do site
incluem React, React DOM, Vite e os plugins de ESLint.

## Instalação

Na raiz do repositório:

```powershell
uv sync
```

Na pasta do site:

```powershell
cd frontend
npm install
```

## Executando a API

Em um terminal, na raiz:

```powershell
uv run uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Também é possível iniciar diretamente:

```powershell
uv run python api.py
```

O endpoint de processamento é:

```text
POST /
Content-Type: multipart/form-data
Campo: file
```

Formatos aceitos: JPG, JPEG, PNG, BMP e WEBP. A resposta contém:

```json
{
  "pseudocode": "texto reconhecido",
  "python": "código Python convertido",
  "output": "saída da execução",
  "error": null
}
```

Quando ocorre uma falha, `error` contém a mensagem em português. A
documentação interativa fica em `http://localhost:8000/docs`.

## Executando o site React

Com a API em execução, abra outro terminal:

```powershell
cd frontend
npm run dev
```

O Vite informa a URL local, normalmente `http://localhost:5173`.

O site usa `http://localhost:8000/` por padrão. Para alterar a URL da API,
crie `frontend/.env`:

```env
VITE_API_URL=http://192.168.0.10:8000/
```

Comandos disponíveis no `frontend/package.json`:

```powershell
npm run dev       # servidor de desenvolvimento
npm run build     # build de produção em frontend/dist
npm run preview   # servir o build localmente
npm run lint      # ESLint
```

A fonte `JetBrains Mono` usada nas caixas de código está em
`frontend/src/assets/JetBrainsMonoNL-Bold.ttf`.

## Executando a interface desktop

Na raiz do repositório:

```powershell
uv run python interface.py
```

A interface permite escolher uma imagem avulsa ou uma pasta de imagens,
selecionar o arquivo, visualizar o preview e processar o algoritmo localmente,
sem depender da API.

## Testes

Os testes existentes podem ser executados pela raiz com:

```powershell
uv run pytest
```

Os arquivos `tests/core.py` e `tests/core_multiple.py` cobrem o processamento
do núcleo. `tests/api.py` e `tests/api_multiple.py` cobrem o processamento
pela API. `tests/results.json` contém os dados de referência usados pelos
testes com múltiplas imagens.

## Funcionamento interno

1. `api.py` valida a extensão ou o MIME type e salva o upload temporariamente.
2. `core.reader` detecta os ArUco, corrige a orientação e ordena os blocos.
3. `core.converter` limpa o texto e gera o pseudocódigo indentado e o Python.
4. `core.interpreter` monta a árvore de comandos e interpreta o algoritmo sem
   executar texto arbitrário via `exec`.
5. `core.pipeline` padroniza a resposta com `pseudocode`, `python`, `output` e
   `error`.
6. A API remove o arquivo temporário após o processamento.

O interpretador suporta variáveis, expressões aritméticas, comparadores,
condicionais (`se`, `senao se`, `senao`), repetições (`repita`) e laços
(`enquanto`), de acordo com os blocos definidos em `core/blocks.json`.

## Blocos físicos

`blocks/blocks.json` relaciona cada ID do marcador com uma palavra do
pseudocódigo. `blocks/arucos/` contém as imagens dos marcadores. Para gerar ou
atualizar os marcadores:

```powershell
uv run python blocks/generator.py
```

`blocks/blocks.pdf` contém os blocos prontos para impressão e
`blocks/problems.pdf` contém exercícios para montagem e teste dos algoritmos.

## Licença

Consulte o arquivo [LICENSE](LICENSE).
