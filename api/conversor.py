from re import sub

PSEUDO_INDENT = 2
PYTHON_INDENT = 4


def getKeyword(tokens: list[str], /) -> tuple[str, list[str]]:
    """Extrai a palavra-chave e os argumentos restantes de uma lista de tokens.

    Identifica palavras-chaves compostas por dois tokens (como "senao se" ou
    "fim <bloco>") e as separa do restante dos tokens da linha.

    Args:
        tokens (list[str]): Lista de palavras/tokens de uma linha do pseudocódigo.

    Returns:
        tuple[str, list[str]]: Uma tupla contendo:
            - A palavra-chave identificada (str).
            - A lista dos tokens restantes/argumentos (list[str]).
    """
    if len(tokens) >= 2 and tokens[0] == "senao" and tokens[1] == "se":
        return "senao se", tokens[2:]

    if len(tokens) >= 2 and tokens[0] == "fim":
        return " ".join(tokens[:2]), tokens[2:]

    return tokens[0], tokens[1:]


def indentLevels(lines: list[str], /) -> list[int]:
    """Calcula os níveis de indentação para cada linha de pseudocódigo.

    Percorre as linhas do código rastreando a abertura ("inicio", "se", "repita",
    "enquanto") e o fechamento ("fim", "fim se", etc.) de blocos.

    Args:
        lines (list[str]): Lista de linhas contendo as instruções do pseudocódigo.

    Returns:
        list[int]: Lista de inteiros com o nível de profundidade/indentação de cada linha.
    """
    level = 0
    levels = []

    for line in lines:
        tokens = line.split()
        kw, _ = getKeyword(tokens)

        if kw in {"fim", "fim se", "fim repita", "fim enquanto"}:
            level -= 1

        levels.append(max(level, 0))

        if kw in {"inicio", "se", "repita", "enquanto"}:
            level += 1

    return levels


def indentPseudo(pseudocode: str, /) -> str:
    """Formata e aplica a indentação adequada a um texto em pseudocódigo.

    Garante a presença dos delimitadores principais ("inicio" no começo e "fim"
    no final) e insere os espaços de indentação configurados em `PSEUDO_INDENT`.

    Args:
        pseudocode (str): O código-fonte em pseudocódigo sem formatação.

    Returns:
        str: O pseudocódigo devidamente indentado e formatado.
    """
    lines = pseudocode.split("\n")
    if lines[0] != "inicio":
        lines.insert(0, "inicio")
    if lines[-1] != "fim":
        lines.append("fim")
    levels = indentLevels(lines)

    result = []

    for line, level in zip(lines, levels):
        result.append(" " * (level * PSEUDO_INDENT) + line)

    return "\n".join(result)


def exprToPython(expr: str, /) -> str:
    """Converte expressões e palavras reservadas do pseudocódigo para a sintaxe Python.

    Substitui os valores booleanos 'verdadeiro' -> 'True' e 'falso' -> 'False'.

    Args:
        expr (str): Expressão em pseudocódigo a ser traduzida.

    Returns:
        str: Expressão convertida para a sintaxe válida em Python.
    """
    expr = sub(r"\bverdadeiro\b", "True", expr)
    expr = sub(r"\bfalso\b", "False", expr)
    return expr


def toPython(pseudocode: str, /) -> str:
    """Traduz um programa escrito em pseudocódigo para código-fonte Python executável.

    Analisa a estrutura, calcula indentações e converte palavras-chave
    (como 'vale', 'mostre', 'se', 'enquanto', 'repita') para suas instruções
    equivalentes em Python.

    Args:
        pseudocode (str): O código completo em pseudocódigo.

    Returns:
        str: Código traduzido em Python formatado e indentado.
    """
    lines = [l.strip() for l in pseudocode.split("\n") if l.strip()]
    levels = [max(n - 1, 0) for n in indentLevels(lines)]

    python_lines = []

    for line, level in zip(lines, levels):
        tokens = line.split()
        kw, args = getKeyword(tokens)

        indent = " " * (level * PYTHON_INDENT)

        if "vale" in line:
            var, valor = line.split("vale", 1)
            python_lines.append(
                f"{indent}{var.strip()} = {exprToPython(valor.strip())}"
            )

        elif kw == "mostre":
            python_lines.append(f"{indent}print({exprToPython(' '.join(args))})")

        elif kw == "se":
            python_lines.append(f"{indent}if {exprToPython(' '.join(args))}:")

        elif kw == "senao se":
            python_lines.append(f"{indent}elif {exprToPython(' '.join(args))}:")

        elif kw == "senao":
            python_lines.append(f"{indent}else:")

        elif kw == "enquanto":
            python_lines.append(f"{indent}while {exprToPython(' '.join(args))}:")

        elif kw == "repita":
            python_lines.append(
                f"{indent}for _ in range({exprToPython(' '.join(args))}):"
            )

    return "\n".join(python_lines)
