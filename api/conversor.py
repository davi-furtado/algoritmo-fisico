from re import sub

PSEUDO_INDENT = 2
PYTHON_INDENT = 4

def getKeyword(tokens):
    if len(tokens) >= 2 and tokens[0] == 'senao' and tokens[1] == 'se':
        return 'senao se', tokens[2:]

    if len(tokens) >= 2 and tokens[0] == 'fim':
        return ' '.join(tokens[:2]), tokens[2:]

    return tokens[0], tokens[1:]


def indentLevels(lines):
    level = 0
    levels = []

    for line in lines:
        tokens = line.split()
        kw, _ = getKeyword(tokens)

        if kw in {'fim se', 'fim repita', 'fim enquanto', 'fim'}:
            level -= 1

        levels.append(max(level, 0))

        if kw in {'inicio', 'se', 'repita', 'enquanto'}:
            level += 1

    return levels


def indentPseudo(pseudocode):
    lines = pseudocode.split('\n')
    if lines[0] != 'inicio': lines[0] = 'inicio'
    if lines[-1] != 'fim': lines.append('fim')
    levels = indentLevels(lines)

    result = []

    for line, level in zip(lines, levels):
        result.append(' ' * (level * PSEUDO_INDENT) + line)

    return '\n'.join(result)


def exprToPython(expr):
    expr = sub(r'\bverdadeiro\b', 'True', expr)
    expr = sub(r'\bfalso\b', 'False', expr)
    return expr


def toPython(pseudocode):
    lines = [l.strip() for l in pseudocode.split('\n') if l.strip()]
    levels = [max(n-1, 0) for n in indentLevels(lines)]

    python_lines = []

    for line, level in zip(lines, levels):
        tokens = line.split()
        kw, args = getKeyword(tokens)

        indent = ' ' * (level * PYTHON_INDENT)

        if 'vale' in line:
            var, valor = line.split('vale', 1)
            python_lines.append(
                f'{indent}{var.strip()} = {exprToPython(valor.strip())}'
            )

        elif kw == 'mostre':
            python_lines.append(
                f'{indent}print({exprToPython(' '.join(args))})'
            )

        elif kw == 'se':
            python_lines.append(
                f'{indent}if {exprToPython(' '.join(args))}:'
            )

        elif kw == 'senao se':
            python_lines.append(
                f'{indent}elif {exprToPython(' '.join(args))}:'
            )

        elif kw == 'senao':
            python_lines.append(f'{indent}else:')

        elif kw == 'enquanto':
            python_lines.append(
                f'{indent}while {exprToPython(' '.join(args))}:'
            )

        elif kw == 'repita':
            python_lines.append(
                f'{indent}for _ in range({exprToPython(' '.join(args))}):'
            )

    return '\n'.join(python_lines)