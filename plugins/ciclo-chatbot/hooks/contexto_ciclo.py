#!/usr/bin/env python3
"""SessionStart do ciclo-chatbot.

Se o projeto tiver .ciclo-chatbot/estado.md, imprime um resumo curto
(fase atual e próximo passo) que o Claude Code adiciona ao contexto.
Em qualquer outro projeto, não imprime nada.
"""
import json
import os
import sys


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    path = os.path.join(root, ".ciclo-chatbot", "estado.md")
    if not os.path.isfile(path):
        return 0

    fase = proximo = None
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s.startswith("Fase atual:"):
                    fase = s
                elif s.startswith("Próximo passo:"):
                    proximo = s
    except OSError:
        return 0

    linhas = ["Este projeto segue o ciclo-chatbot (estado em .ciclo-chatbot/estado.md)."]
    if fase:
        linhas.append(fase)
    if proximo:
        linhas.append(proximo)
    linhas.append("Para continuar o fluxo, use a skill ciclo-chatbot:iniciar.")
    print("\n".join(linhas))
    return 0


if __name__ == "__main__":
    sys.exit(main())
