<div align="center">
  <h1>APP Algoritmo Físico</h1>

  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi">
  <img src="https://img.shields.io/badge/react_native-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB">
  <img src="https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E">
  <img src="https://img.shields.io/badge/CustomTkinter-222528?style=for-the-badge&logo=python&logoColor=white">
</div>

<p align="center">
Aplicativo que escaneia pseudocódigos em blocos (algoritmos físicos) a partir de imagens e retorna o código equivalente em <b>Python</b> junto com a <b>saída da execução</b>.
</p>

<hr>

## 📋 Sumário

- [✨ Funcionalidades](#-funcionalidades)
- [📂 Estrutura do Projeto](#-estrutura-do-projeto)
  - [Interface Desktop](#interface-desktop)
  - [Mobile](#mobile)
  - [API](#api)
- [🚀 Como rodar?](#-como-rodar)
  - [Interface Desktop](#interface-desktop-1)
  - [API](#api-1)
  - [Mobile](#mobile-1)
- [🧱 Pasta de blocos físicos](#-pasta-de-blocos-físicos)
- [🔄 Fluxo de funcionamento](#-fluxo-de-funcionamento)
- [⚙️ Conversão de pseudocódigo](#-conversão-de-pseudocódigo)
- [🧪 Pasta de testes](#-pasta-de-testes)
- [📤 Exemplo de retorno da API](#-exemplo-de-retorno-da-api)
- [🌐 Próximos Passos (Deploy)](#-próximos-passos-deploy)

<hr>

# ✨ Funcionalidades

- Captura de imagem pela câmera ou galeria (mobile)
- Seleção de imagem ou pasta com imagens (desktop)
- Reconhecimento de marcadores **ArUco**
- Conversão do pseudocódigo para Python
- Execução do código gerado
- Retorno do código e da saída (ou erro)
- Indentação automática do pseudocódigo
- Indentação automática do Python gerado
- Visualização ampliada da imagem capturada (mobile)
- **Preview da imagem** na interface, com opção de clicar para abrir no visualizador padrão do sistema (desktop)
- Pseudocódigo e Python exibidos **lado a lado** (desktop)
- Geração de executável `.exe` via PyInstaller (desktop)

# 📂 Estrutura do Projeto

<details>
  <summary>FileTree</summary>

```
app-algoritmo-fisico/
│
├── api/
│   ├── aruco_reader.py
│   ├── blocks.json
│   ├── conversor.py
│   ├── executor.py
│   ├── main.py
│   ├── mono_return.py
│   └── requirements.txt
│
├── api_tests/
│   ├── pics/
│   │   ├── img1.jpg
│   │   ├── img2.jpg
│   │   └── ...
│   │
│   ├── multiple_test.py
│   ├── requirements.txt
│   ├── results.json
│   └── test.py
│
├── blocks/
│   ├── arucos/
│   │   ├── ...
│   │   ├── 21_verdadeiro.png
│   │   ├── 22_falso.png
│   │   ├── 23_inicio.png
│   │   ├── 24_fim.png
│   │   ├── 25_mostre.png
│   │   ├── 26_vale.png
│   │   └── ...
│   │
│   ├── blocks.json
│   ├── generator.py
│   ├── problems.pdf
│   └── requirements.txt
│
├── interface/
│   ├── dist/
│   │   └── main.exe
│   │
│   ├── aruco_reader.py
│   ├── blocks.json
│   ├── conversor.py
│   ├── executor.py
│   ├── img_reader.py
│   ├── main.py
│   ├── pyinstaller_command.txt
│   ├── requirements.txt
│   └── utils.py
│
├── mobile/
│   ├── assets/
│   │   ├── images/
│   │   │   ├── adaptive-icon.png
│   │   │   ├── favicon.png
│   │   │   ├── icon.png
│   │   │   └── splash-icon.png
│   │   │
│   │   └── JetBrainsMonoNL-Bold.ttf
│   │
│   ├── components/
│   │   ├── CodeBox.jsx
│   │   ├── InsertPhotoBtn.jsx
│   │   └── SegmentedToggle.jsx
│   │
│   ├── app.json
│   ├── App.jsx
│   ├── index.js
│   ├── package-lock.json
│   ├── package.json
│   └── styles.js
│
├── .gitignore
└── README.md
```

Filetree gerada com a biblioteca [`pyletree`](https://github.com/davi-furtado/pyletree)

</details>

## Interface Desktop

Tecnologias utilizadas:

- Python
- CustomTkinter
- OpenCV (ArUco)

Interface gráfica para desktop que processa imagens **localmente**, sem depender da API. Permite:

- Selecionar uma **imagem avulsa** ou uma **pasta com imagens**
- Seletor dropdown para escolher a imagem da pasta
- Exibição do pseudocódigo e Python **lado a lado**
- Caixa de saída com título dinâmico: **"Saída"** em caso de sucesso ou **"Erro"** em caso de falha
- **Preview da imagem** na interface, com opção de clicar para abrir no visualizador padrão do sistema
- Geração de executável `.exe` via PyInstaller

## Mobile

Tecnologias utilizadas:

- React Native
- Expo
- JavaScript

Responsável pela interface do aplicativo móvel, incluindo:

- Captura ou seleção de imagens
- Envio da imagem à API
- Exibição do pseudocódigo reconhecido, Python gerado e saída da execução
- Título dinâmico: **"Saída"** ou **"Erro"** conforme o retorno

## API

Tecnologias utilizadas:

- Python
- FastAPI
- OpenCV (ArUco)

A API é responsável por:

1. Detectar os marcadores ArUco na imagem
2. Reconstruir o pseudocódigo a partir dos marcadores
3. Converter o pseudocódigo em Python
4. Executar o código gerado
5. Retornar o resultado para o aplicativo

### Arquivos principais

#### `main.py`

API FastAPI que atua como ponto de entrada, responsável por:

- Receber a imagem enviada pelo aplicativo
- Orquestrar a detecção, conversão e execução chamando os módulos auxiliares
- Retornar os resultados processados

#### `aruco_reader.py`

Módulo dedicado à visão computacional com OpenCV. Responsável por:

- Detectar os marcadores ArUco na imagem
- Reconstruir o texto do pseudocódigo baseado nas posições espaciais dos identificadores

#### `executor.py`

Ambiente isolado (via `multiprocessing`) projetado para:

- Executar o código Python gerado
- Prevenir loops infinitos ou tempo excessivo de execução através de um mecanismo de **timeout**
- Capturar e interceptar a saída simulando a saída padrão (stdout) e os erros da execução

#### `conversor.py`

Arquivo responsável por converter o pseudocódigo em Python.

#### `blocks.json`

Define o **mapeamento entre IDs dos marcadores ArUco e comandos do pseudocódigo**.

### Arquivos secundários

#### `mono_return.py`

API que tem um retorno único independente da imagem enviada. Pode ser usada para testar conectividade com o front-end sem processar imagens.

#### `requirements.txt`

Arquivo com todas as dependências usadas na API.

# 🚀 Como rodar?

## Requisitos

- Python 3.8 ou superior
- Node.js 14 ou superior (para o mobile)
- npm 6 ou superior (para o mobile)

## Interface Desktop

1. Abra um terminal na pasta `interface`
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute a interface:
   ```bash
   python main.py
   ```

### Gerando o executável

Para gerar um `.exe` standalone, use o PyInstaller dentro da pasta `interface`:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --add-data "blocks.json;." main.py
```

O executável será gerado em `interface/dist/main.exe`. O arquivo `utils.py` é responsável por resolver os caminhos temporários dos arquivos embutidos pelo PyInstaller (como o `blocks.json`).

## API

1. Abra um terminal na pasta `api`
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie a API:
   ```bash
   python main.py
   ```
   ou
   ```bash
   uvicorn main:app --host 0.0.0.0
   ```

## Mobile

1. Crie o arquivo `mobile/.env` e coloque o endereço completo da sua API (incluindo o IP local e porta) na variável `API_URL` para que o aplicativo consiga comunicar com a API localmente. Deve ficar assim:
   ```bash
   API_URL=http://w.x.y.z:8000
   ```
2. Abra um terminal na pasta `mobile`
3. Instale as dependências:
   ```bash
   npm install
   ```
4. Inicie o projeto Expo:
   ```bash
   npx expo start --port 6000
   ```
5. Para rodar no celular, baixe o aplicativo **Expo Go** e escaneie o QR code exibido.

## Usando os scripts de automação

O arquivo `set_env.py` automatiza a criação do arquivo `.env` para o mobile, preenchendo a variável `IP` com o endereço IP local da máquina.

Ele reescreve o arquivo:

- `mobile/.env`

O arquivo `run_all.py` inicia a API e o mobile automaticamente:

- `api` (uvicorn)
- `mobile` (expo start)

Para usar, execute o script na raiz do projeto:

```bash
python run_all.py
```

# 🧱 Pasta de blocos físicos

O projeto possui uma pasta `blocks` com os materiais necessários para utilizar o sistema com **algoritmos físicos**.

## `problems.pdf`

PDF contendo **exercícios de lógica de programação**.

Os alunos podem resolver os problemas **montando algoritmos com os blocos físicos** e depois usar o aplicativo para verificar a solução.

## `blocks.json`

Arquivo que define o **mapeamento entre IDs de ArUco e palavras do pseudocódigo**.

Exemplo simplificado:

```json
{
  "21": "verdadeiro",
  "22": "falso",
  "23": "inicio",
  "24": "fim",
  "25": "mostre",
  "26": "vale"
}
```

Esse arquivo também existe na **API** e na **interface desktop**, onde é utilizado durante o reconhecimento dos blocos.

## `generator.py`

Script responsável por **gerar automaticamente os marcadores ArUco utilizados no projeto**.

Ele cria todas as imagens dentro da pasta `blocks/arucos`.

# 🔄 Fluxo de funcionamento

## Via API (Mobile)

1. O mobile envia uma imagem para o endpoint `/convert`
2. A API usa **OpenCV ArUco** para detectar os marcadores
3. Os **IDs detectados são convertidos em palavras** usando `blocks.json`
4. O pseudocódigo gerado é enviado para `toPython()` (`conversor.py`)
5. O pseudocódigo é transformado em **código Python válido**
6. A API executa o código usando `exec`
7. A API retorna: pseudocódigo reconhecido, código Python gerado e saída da execução

## Via Interface Desktop

1. O usuário seleciona uma imagem ou pasta
2. O `img_reader.py` processa a imagem **localmente** usando os mesmos módulos (`aruco_reader`, `conversor`, `executor`)
3. Os resultados são exibidos diretamente na interface: pseudocódigo e Python lado a lado, com a saída (ou erro) acima

# ⚙️ Conversão de pseudocódigo

O arquivo `conversor.py` implementa um **parser simples baseado em tokens** responsável por:

- Interpretar palavras do pseudocódigo
- Gerar estruturas Python equivalentes
- Controlar níveis de indentação
- Converter expressões e operadores

## Estruturas suportadas

### Condicionais

```
se
senao
senao se
fim se
```

### Repetição

```
repita
fim repita
enquanto
fim enquanto
```

### Saída

```
mostre _____
```

### Variáveis

```
_____ vale __
```

### Operadores e Valores

- **Operadores Matemáticos**: `+`, `-`, `*`, `/`
- **Operadores Relacionais**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Valores Lógicos**: `verdadeiro` e `falso`
- **Valores e Variáveis Pré-definidas**: Números de `0` a `20`, e as variáveis `quantidade`, `valor`, `valor1`, `valor2`, `amigos`, `resto` e `resultado`.

## Indentação automática

O conversor implementa um sistema de **controle de níveis de bloco**, permitindo:

- Indentação correta do pseudocódigo
- Geração de Python com indentação válida

O projeto utiliza:

- 2 espaços para pseudocódigo
- 4 espaços para Python

Isso garante que o código gerado seja **executável imediatamente**.

# 🧪 Pasta de testes

A pasta `api_tests` contém utilitários projetados para validar e debugar a API de conversão de imagens rapidamente, sem a necessidade de rodar o front-end simultaneamente. O ambiente de testes possui seu próprio arquivo `requirements.txt` e uma subpasta `pics/` com imagens de amostra para realizar testes pré-configurados.

## `test.py`

Script simples onde o usuário informa o caminho local de uma imagem por meio da entrada padrão do terminal. O script envia a imagem para o endpoint `/convert` local (porta `8000`) e imprime o JSON retornado pela API na tela.

## `multiple_test.py`

Script iterativo útil para processar e debugar um lote de imagens em sequência. Ele varre uma lista de caminhos de imagens (na variável iterável `paths`), as envia uma por vez para a API e compila os resultados (erros, pseudocódigo gerado e saídas em Python) num arquivo unificado independente chamado `results.json` na própria pasta.

# 📤 Exemplo de retorno da API

```json
{
  "output": "10",
  "pseudocode": "inicio\n  valor vale 10\n  valor1 vale 5\n  se valor > valor1\n    mostre valor\n  senao\n    mostre valor1\n  fim se\nfim",
  "python": "valor = 10\nvalor1 = 5\nif valor > valor1:\n    print(valor)\nelse:\n    print(valor1)"
}
```

# 🌐 Próximos Passos (Deploy)

Como principal evolução do projeto, **pretendemos fazer o deploy na web do site e da API na Vercel**. 

Essa migração permitirá:
- **Acesso Universal:** Qualquer pessoa poderá utilizar o aplicativo diretamente de um navegador (computador ou celular) sem precisar instalar dependências ou rodar o servidor localmente.
- **Integração Fluida:** A Vercel permitirá hospedar tanto o front-end quanto a API FastAPI com alta performance e facilidade de integração contínua (CI/CD).
- **Escalabilidade Educacional:** Mais professores e alunos terão facilidade de adotar a ferramenta nas escolas, utilizando apenas o link da aplicação hospedada.
