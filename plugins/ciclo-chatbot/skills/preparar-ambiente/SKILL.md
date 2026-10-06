---
name: preparar-ambiente
description: Instala e confere as peças da comunidade que o ciclo-chatbot orquestra (plugins, skills, MCPs e CLIs), em camadas: núcleo sempre, e o resto conforme a stack, o provider de WhatsApp e o PaaS escolhidos. Usar quando o usuário disser "preparar ambiente", "instalar dependências do ciclo", "quais plugins da comunidade preciso", "configurar MCPs do chatbot", na fase 0 do /ciclo-chatbot:iniciar, ou quando uma fase precisar de uma peça que não está instalada.
argument-hint: "[nucleo | banco | ia | stack-ts | stack-python | whatsapp | seguranca | deploy-railway | deploy-render | deploy-fly | observabilidade | tudo]"
---

# Preparar ambiente

Instalar só o que a fase precisa, sem peças que se sobrepõem. O catálogo completo, com comandos, licenças e procedência verificada, está em `${CLAUDE_SKILL_DIR}/references/catalogo-comunidade.md`. Ler a seção da camada pedida antes de instalar.

## 1. Descobrir o que já existe

Em Claude Code com shell:

```bash
claude plugin list --json
claude plugin marketplace list
claude mcp list
```

Comparar com o catálogo e montar a lista do que falta para a camada pedida em `$ARGUMENTS` (padrão: `nucleo`). Se o estado do ciclo já registra decisões de stack, provider ou PaaS, usar essas decisões para escolher as camadas.

No Cowork sem shell: listar ao usuário o que falta e como adicionar pelo painel de plugins; seguir com o material de apoio do ciclo-chatbot como fallback.

## 2. Confirmar antes de instalar

Mostrar ao usuário uma tabela curta (peça, para que serve, origem, licença) e pedir confirmação com AskUserQuestion. Instalar com escopo de projeto por padrão (`--scope project`), para que o time compartilhe a mesma configuração em `.claude/settings.json`. Respeitar se o usuário preferir escopo de usuário.

## 3. Instalar

- Marketplace de terceiros: `claude plugin marketplace add <owner/repo> --scope project`, depois `claude plugin install <plugin>@<marketplace> --scope project`.
- Marketplace oficial (`claude-plugins-official`) já vem configurado: só o `install`.
- MCP com credencial: `claude mcp add --scope local ...` para o segredo não ir para o repositório. Se o time precisar compartilhar, usar `--scope project` com `${VARIAVEL}` no lugar do valor e documentar a variável no README do projeto.
- CLIs (Squawk, jscpd, promptfoo, k6, CLI do PaaS, cloudflared): conferir com `which` antes; instalar só com o aceite do usuário.

Rodar um comando por vez e conferir a saída. Se um install falhar, registrar o erro e o fallback no estado e seguir; não insistir no mesmo comando.

## 4. Recarregar e conferir

Plugins novos podem exigir reiniciar a sessão para as skills aparecerem. Avisar o usuário quando for o caso. Depois, conferir que as skills e agentes esperados aparecem na lista disponível e que os MCPs respondem (`/mcp`).

## 5. Registrar

Atualizar a tabela "Peças da comunidade em uso" em `.ciclo-chatbot/estado.md`: peça, fase, instalada ou não, fallback usado.

## Regras de sobreposição

- Revisão de código: usar `pr-review-toolkit` e não instalar também `code-review` nem `code-simplifier` avulso.
- TDD: superpowers `test-driven-development` já cobre; `tdd-guard` só se o usuário quiser bloqueio automático.
- `backend-architect` e `security-auditor` aparecem em vários plugins do wshobson: instalar só os plugins listados no catálogo.
- Context7 já vem no `.mcp.json` deste plugin: não instalar o plugin `context7` em paralelo.
- Playwright só se o projeto tiver painel web; o chatbot em si não precisa.
