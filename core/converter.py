"""
converter.py — organiza o pseudocódigo lido e gera o Python equivalente.

IMPORTANTE: aqui o Python gerado serve APENAS para ser mostrado na tela, com
valor pedagógico ("olha como ficaria isso escrito de verdade"). Quem executa o
algoritmo é o interpreter.py, que não usa exec() nem gera código.

Novidade em relação ao converter.py original: a função clean(), que resolve
duas situações que apareciam nas fotos reais de sala de aula.

  a) O bloco "inicio" ou "fim" fotografado ao lado de um comando, na mesma
     altura da mesa, virava uma linha só ("inicio quantidade vale 3"), que o
     converter não conseguia interpretar.

  b) Blocos soltos largados perto do algoritmo entravam na leitura como se
     fossem parte dele (um "-" perdido, um "fim se" sobrando).
"""

import re

RECUO_PSEUDO = 2
RECUO_PYTHON = 4

ABREM_BLOCO = {"inicio", "se", "repita", "enquanto"}
FECHAM_BLOCO = {"fim", "fim se", "fim repita", "fim enquanto"}

COMANDOS = {
    "inicio", "fim",
    "mostre",
    "se", "senao", "senao se", "fim se",
    "repita", "fim repita",
    "enquanto", "fim enquanto",
}


def keyword(tokens):
    """Devolve (comando, argumentos) a partir dos tokens de uma linha."""
    if not tokens:
        return "", []

    if len(tokens) >= 2 and tokens[0] == "senao" and tokens[1] == "se":
        return "senao se", tokens[2:]

    if len(tokens) >= 2 and tokens[0] == "fim":
        return " ".join(tokens[:2]), tokens[2:]

    return tokens[0], tokens[1:]


def clean(pseudocode):
    """
    Separa 'inicio'/'fim' em linhas próprias e descarta linhas que não formam
    nenhum comando reconhecível (blocos soltos na mesa).
    """
    if not pseudocode:
        return ""

    texto = re.sub(r"\binicio\b", "\ninicio\n", pseudocode)
    # 'fim' sozinho vira linha própria; 'fim se/repita/enquanto' fica intacto
    texto = re.sub(r"\bfim\b(?!\s+(?:se|repita|enquanto)\b)", "\nfim\n", texto)

    validas = []
    for linha in texto.split("\n"):
        linha = linha.strip()
        if not linha:
            continue
        comando, _ = keyword(linha.split())
        if comando in COMANDOS or "vale" in linha.split():
            validas.append(linha)

    # O algoritmo é o que está entre o "inicio" e o "fim". Blocos soltos
    # largados antes ou depois na mesa são descartados aqui.
    if "inicio" in validas:
        validas = validas[validas.index("inicio"):]
    if "fim" in validas:
        ultimo = len(validas) - 1 - validas[::-1].index("fim")
        validas = validas[:ultimo + 1]

    return "\n".join(validas)


def indentation_levels(lines):
    nivel = 0
    niveis = []

    for linha in lines:
        comando, _ = keyword(linha.split())

        if comando in FECHAM_BLOCO:
            nivel -= 1

        niveis.append(max(nivel, 0))

        if comando in ABREM_BLOCO:
            nivel += 1

    return niveis


def indent_pseudocode(pseudocode):
    """Aplica o recuo visual ao pseudocódigo. Garante 'inicio' e 'fim'."""
    linhas = [l.strip() for l in pseudocode.split("\n") if l.strip()]
    if not linhas:
        return ""

    if linhas[0] != "inicio":
        linhas.insert(0, "inicio")
    if linhas[-1] != "fim":
        linhas.append("fim")

    niveis = indentation_levels(linhas)
    return "\n".join(
        " " * (n * RECUO_PSEUDO) + l for l, n in zip(linhas, niveis)
    )


def _expr_para_python(expressao):
    expressao = re.sub(r"\bverdadeiro\b", "True", expressao)
    expressao = re.sub(r"\bfalso\b", "False", expressao)
    return expressao


def to_python(pseudocode):
    """Gera o Python equivalente, apenas para exibição na tela."""
    linhas = [l.strip() for l in pseudocode.split("\n") if l.strip()]
    niveis = [max(n - 1, 0) for n in indentation_levels(linhas)]

    resultado = []

    for linha, nivel in zip(linhas, niveis):
        tokens = linha.split()
        comando, argumentos = keyword(tokens)
        recuo = " " * (nivel * RECUO_PYTHON)
        args = " ".join(argumentos)

        if "vale" in tokens:
            variavel, valor = linha.split("vale", 1)
            resultado.append(
                f"{recuo}{variavel.strip()} = {_expr_para_python(valor.strip())}"
            )
        elif comando == "mostre":
            resultado.append(f"{recuo}print({_expr_para_python(args)})")
        elif comando == "se":
            resultado.append(f"{recuo}if {_expr_para_python(args)}:")
        elif comando == "senao se":
            resultado.append(f"{recuo}elif {_expr_para_python(args)}:")
        elif comando == "senao":
            resultado.append(f"{recuo}else:")
        elif comando == "enquanto":
            resultado.append(f"{recuo}while {_expr_para_python(args)}:")
        elif comando == "repita":
            resultado.append(f"{recuo}for _ in range({_expr_para_python(args)}):")

    return "\n".join(resultado)
