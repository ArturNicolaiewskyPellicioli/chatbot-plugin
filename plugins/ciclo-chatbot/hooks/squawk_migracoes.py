#!/usr/bin/env python3
"""PostToolUse do ciclo-chatbot: lint de migrações SQL com o Squawk.

Roda só quando o arquivo gravado é .sql e está numa pasta de migrações
(migrations, migration, migrate, drizzle, alembic). Se o Squawk não estiver
instalado, não faz nada. Com alertas, sai com código 2 e devolve a saída ao
Claude para correção.
"""
import json
import os
import re
import shutil
import subprocess
import sys

PASTA_MIGRACAO = re.compile(r"(^|[\\/])(migrations?|migrate|drizzle|alembic)([\\/]|$)", re.IGNORECASE)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    tool_input = data.get("tool_input") or {}
    path = tool_input.get("file_path") or ""
    if not path.lower().endswith(".sql") or not PASTA_MIGRACAO.search(path):
        return 0

    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    if not os.path.isabs(path):
        path = os.path.join(root, path)
    if not os.path.isfile(path):
        return 0

    squawk = shutil.which("squawk")
    if not squawk:
        return 0

    # Roda na raiz do projeto para o Squawk achar o .squawk.toml (pg_version,
    # assume_in_transaction, regras excluídas). Saída compacta, sem cores.
    try:
        result = subprocess.run(
            [squawk, "--reporter", "gcc", path],
            capture_output=True,
            text=True,
            timeout=50,
            cwd=root if os.path.isdir(root) else None,
        )
    except Exception:
        return 0

    if result.returncode != 0:
        saida = (result.stdout + result.stderr).strip()
        sys.stderr.write(
            f"Squawk encontrou problemas em {path}.\n"
            "Corrija a migração ou justifique cada alerta no documento da fase 3 "
            "(regras em skills/modelar-banco/references/migracoes-seguras.md do ciclo-chatbot).\n\n"
            f"{saida[:6000]}\n"
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
