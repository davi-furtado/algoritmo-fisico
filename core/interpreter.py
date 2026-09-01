"""
interpreter.py - executa o pseudocódigo diretamente, sem gerar nem rodar
código Python.

POR QUE ISSO SUBSTITUI O executor.py ORIGINAL

O executor antigo montava um texto em Python, chamava exec() para rodá-lo e
usava multiprocessing para poder matar o processo caso o algoritmo entrasse em
laço infinito. Três problemas:

  1. multiprocessing não funciona de forma confiável dentro de um app Android.
     Só isso já inviabilizaria o app.
  2. exec() executa qualquer coisa que estiver no texto. Num app distribuído
     para escolas, isso é uma porta aberta que não precisa existir.
  3. Quando algo dava errado, a criança via a mensagem de erro do Python
     ("unexpected indent", "invalid syntax"), que não significa nada para ela.

Aqui o pseudocódigo é interpretado passo a passo. O laço infinito é controlado
por um contador de passos, sem precisar de processo separado. E os erros saem
em português, apontando o que faltou.
"""

LIMITE_PASSOS = 200_000
LIMITE_LINHAS_SAIDA = 200


class ErroDeAlgoritmo(Exception):
    """Erro que a criança precisa entender: falta um bloco, sobra um bloco."""


# --------------------------------------------------------------------------
# Avaliação de expressões
# --------------------------------------------------------------------------

COMPARADORES = {"==", "!=", "<", ">", "<=", ">="}
ADITIVOS = {"+", "-"}
MULTIPLICATIVOS = {"*", "/", "%", "//"}


def _valor_do_token(token, variaveis):
    if token == "verdadeiro":
        return True
    if token == "falso":
        return False
    if token.lstrip("-").isdigit():
        return int(token)
    if token in variaveis:
        return variaveis[token]
    raise ErroDeAlgoritmo(f'O bloco "{token}" foi usado antes de receber um valor.')


def _aplicar(operador, a, b):
    try:
        if operador == "+":
            return a + b
        if operador == "-":
            return a - b
        if operador == "*":
            return a * b
        if operador == "/":
            return a / b
        if operador == "//":
            return a // b
        if operador == "%":
            return a % b
        if operador == "==":
            return a == b
        if operador == "!=":
            return a != b
        if operador == "<":
            return a < b
        if operador == ">":
            return a > b
        if operador == "<=":
            return a <= b
        if operador == ">=":
            return a >= b
    except ZeroDivisionError:
        raise ErroDeAlgoritmo("Não é possível dividir por zero.")
    except TypeError:
        raise ErroDeAlgoritmo(
            f'Não dá para usar "{operador}" entre esses dois valores.'
        )
    raise ErroDeAlgoritmo(f'Operador desconhecido: "{operador}".')


def _avaliar_nivel(tokens, variaveis, operadores, proximo_nivel):
    valor = proximo_nivel(tokens, variaveis)
    while tokens and tokens[0] in operadores:
        operador = tokens.pop(0)
        direita = proximo_nivel(tokens, variaveis)
        valor = _aplicar(operador, valor, direita)
    return valor


def _termo(tokens, variaveis):
    if not tokens:
        raise ErroDeAlgoritmo("Falta um valor no final da expressão.")
    return _valor_do_token(tokens.pop(0), variaveis)


def _produto(tokens, variaveis):
    return _avaliar_nivel(tokens, variaveis, MULTIPLICATIVOS, _termo)


def _soma(tokens, variaveis):
    return _avaliar_nivel(tokens, variaveis, ADITIVOS, _produto)


def avaliar(tokens, variaveis):
    """Avalia uma expressão já quebrada em tokens."""
    restante = list(tokens)
    if not restante:
        raise ErroDeAlgoritmo("Faltou a expressão depois do comando.")
    valor = _avaliar_nivel(restante, variaveis, COMPARADORES, _soma)
    if restante:
        raise ErroDeAlgoritmo(f'Sobrou o bloco "{restante[0]}" no final da linha.')
    return valor


# --------------------------------------------------------------------------
# Montagem da árvore de comandos
# --------------------------------------------------------------------------


def _separar(linha):
    tokens = linha.split()
    if len(tokens) >= 2 and tokens[0] == "senao" and tokens[1] == "se":
        return "senao se", tokens[2:]
    if len(tokens) >= 2 and tokens[0] == "fim":
        return " ".join(tokens[:2]), tokens[2:]
    return (tokens[0], tokens[1:]) if tokens else ("", [])


CONTROLE = {
    "inicio",
    "fim",
    "se",
    "senao",
    "senao se",
    "fim se",
    "repita",
    "fim repita",
    "enquanto",
    "fim enquanto",
}

FECHADORES = {"fim", "fim se", "fim repita", "fim enquanto"}


def _limpar_expressao(tokens):
    """
    Descarta blocos de controle grudados no fim de uma expressão.

    Nas fotos de sala de aula é comum um bloco solto ("senao se", "fim
    enquanto") ficar encostado na linha do comando. Como nenhuma palavra de
    controle pode fazer parte de uma conta, tudo que sobra no fim e é
    palavra de controle é bloco perdido, não parte do algoritmo.
    """
    limpos = list(tokens)
    while limpos and limpos[-1] in CONTROLE:
        limpos.pop()
    return limpos


def _fechar(linhas, posicao, esperado, abertura):
    """
    Confere se o bloco foi fechado. Aceita o fechador certo ("fim repita") ou
    o "fim" genérico. No caso do "fim", a linha NÃO é consumida: ela precisa
    continuar visível para os blocos de fora se fecharem também.
    """
    if posicao >= len(linhas):
        raise ErroDeAlgoritmo(
            f'O "{abertura}" foi aberto mas nunca fechado. '
            f'Faltou o bloco "{esperado}" na foto.'
        )

    atual = _separar(linhas[posicao])[0]

    if atual == esperado:
        return posicao + 1
    if atual == "fim":
        return posicao

    raise ErroDeAlgoritmo(f'Faltou o bloco "{esperado}" para fechar o "{abertura}".')


def montar(linhas, posicao=0, dentro_de=None):
    """
    Transforma a lista de linhas numa árvore de comandos.
    Devolve (lista_de_comandos, proxima_posicao).

    O "fim" é tolerante: ele fecha qualquer bloco que ainda esteja aberto.
    Isso porque, na prática, as crianças fecham o algoritmo inteiro com um
    único bloco "fim" em vez de usar "fim repita" e depois "fim". Quando um
    bloco interno se fecha com "fim", ele não consome a linha, deixando que
    os blocos de fora se fechem também, em cascata.
    """
    comandos = []

    while posicao < len(linhas):
        linha = linhas[posicao]
        comando, argumentos = _separar(linha)

        if comando in FECHADORES or comando in ("senao", "senao se"):
            if dentro_de is None and comando != "fim":
                # Fechador sobrando, sem nada aberto para fechar: bloco solto.
                posicao += 1
                continue
            return comandos, posicao

        if comando == "inicio":
            posicao += 1
            continue

        if "vale" in linha.split():
            variavel, expressao = linha.split("vale", 1)
            nome = variavel.strip()
            if not nome:
                raise ErroDeAlgoritmo('Falta o bloco da variável antes de "vale".')
            comandos.append(("atribuir", nome, _limpar_expressao(expressao.split())))
            posicao += 1

        elif comando == "mostre":
            comandos.append(("mostrar", _limpar_expressao(argumentos)))
            posicao += 1

        elif comando == "se":
            argumentos = _limpar_expressao(argumentos)
            corpo, posicao = montar(linhas, posicao + 1, "se")
            ramos = [(argumentos, corpo)]
            senao = None

            while posicao < len(linhas):
                atual, args_atual = _separar(linhas[posicao])
                if atual == "senao se":
                    corpo, posicao = montar(linhas, posicao + 1, "se")
                    ramos.append((_limpar_expressao(args_atual), corpo))
                elif atual == "senao":
                    senao, posicao = montar(linhas, posicao + 1, "se")
                else:
                    break

            posicao = _fechar(linhas, posicao, "fim se", "se")
            comandos.append(("se", ramos, senao))

        elif comando == "repita":
            corpo, posicao = montar(linhas, posicao + 1, "repita")
            posicao = _fechar(linhas, posicao, "fim repita", "repita")
            comandos.append(("repita", _limpar_expressao(argumentos), corpo))

        elif comando == "enquanto":
            corpo, posicao = montar(linhas, posicao + 1, "enquanto")
            posicao = _fechar(linhas, posicao, "fim enquanto", "enquanto")
            comandos.append(("enquanto", _limpar_expressao(argumentos), corpo))

        else:
            raise ErroDeAlgoritmo(f'Não entendi o bloco "{linha.strip()}".')

    if dentro_de is not None:
        raise ErroDeAlgoritmo(f'O "{dentro_de}" foi aberto mas nunca fechado.')

    return comandos, posicao


# --------------------------------------------------------------------------
# Execução
# --------------------------------------------------------------------------


class _Estado:
    def __init__(self):
        self.variaveis = {}
        self.saida = []
        self.passos = 0
        self.interrompido = False

    def passo(self):
        self.passos += 1
        if self.passos > LIMITE_PASSOS:
            self.interrompido = True
            raise _Interrompido()


class _Interrompido(Exception):
    pass


def _formatar(valor):
    if valor is True:
        return "verdadeiro"
    if valor is False:
        return "falso"
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor)


def _executar(comandos, estado):
    for comando in comandos:
        estado.passo()
        tipo = comando[0]

        if tipo == "atribuir":
            _, nome, expressao = comando
            estado.variaveis[nome] = avaliar(expressao, estado.variaveis)

        elif tipo == "mostrar":
            valor = avaliar(comando[1], estado.variaveis)
            if len(estado.saida) < LIMITE_LINHAS_SAIDA:
                estado.saida.append(_formatar(valor))

        elif tipo == "se":
            _, ramos, senao = comando
            for condicao, corpo in ramos:
                if avaliar(condicao, estado.variaveis):
                    _executar(corpo, estado)
                    break
            else:
                if senao is not None:
                    _executar(senao, estado)

        elif tipo == "repita":
            _, quantidade, corpo = comando
            vezes = avaliar(quantidade, estado.variaveis)
            if not isinstance(vezes, int):
                raise ErroDeAlgoritmo('O "repita" precisa de um número de vezes.')
            for _ in range(max(vezes, 0)):
                estado.passo()
                _executar(corpo, estado)

        elif tipo == "enquanto":
            _, condicao, corpo = comando
            while avaliar(condicao, estado.variaveis):
                estado.passo()
                _executar(corpo, estado)


def execute(pseudocode):
    """
    Executa o pseudocódigo. Devolve (saida, erro).
    Só um dos dois vem preenchido.
    """
    linhas = [l.strip() for l in pseudocode.split("\n") if l.strip()]
    if not linhas:
        return "", "Nenhum bloco foi reconhecido na foto."

    estado = _Estado()

    try:
        comandos, _ = montar(linhas)
        _executar(comandos, estado)
    except _Interrompido:
        texto = "\n".join(estado.saida[:8])
        aviso = "O algoritmo não parou sozinho - parece um laço infinito."
        return (texto + "\n..." if texto else ""), aviso
    except ErroDeAlgoritmo as erro:
        return "", str(erro)
    except RecursionError:
        return "", "O algoritmo ficou fundo demais e precisou ser interrompido."

    if len(estado.saida) >= LIMITE_LINHAS_SAIDA:
        return "\n".join(estado.saida[:LIMITE_LINHAS_SAIDA]) + "\n...", None

    return "\n".join(estado.saida), None
