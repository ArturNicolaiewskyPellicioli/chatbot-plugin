---
name: implementar
description: Implementa o chatbot em fatias verticais com o fluxo do superpowers (plano escrito, TDD, desenvolvimento por subagentes, verificação com evidência), revisão de código do pr-review-toolkit e um revisor de modularidade que bloqueia funções duplicadas e violações de fronteira entre módulos, começando por um esqueleto ponta a ponta webhook → banco → resposta. Usar quando o usuário disser "implementar o bot", "começar o código", "próxima fatia", "esqueleto do projeto", "scaffold", ou na fase 6 do /ciclo-chatbot:iniciar.
argument-hint: "[fatia N | próxima]"
---

# Implementação

Pré-requisito: fases 2 a 5 aprovadas. Estrutura de pastas, regras de dependência, ambiente local e lista de fatias em `${CLAUDE_SKILL_DIR}/references/estrutura-modular.md`.

## Regras que valem para todo código

1. **Uma função, um lugar.** Antes de escrever uma função, procurar (Grep) por nome e por comportamento; se existir, reaproveitar ou mover para o módulo certo. Utilitários compartilhados ficam em `shared/` e nada é copiado entre módulos.
2. **Fronteiras verificadas por ferramenta**, não por disciplina: `dependency-cruiser` ou `eslint-plugin-boundaries` (TypeScript), `import-linter` (Python), rodando no CI.
3. **Nada de provider fora de `adapters/`** e nada de SQL fora da camada de dados.
4. **Configuração validada no boot** (zod, pydantic-settings); o processo não sobe com variável faltando.
5. **Erros não são engolidos**: todo `catch` trata, registra com contexto ou propaga.
6. **Fatos de API conferidos na hora** com Context7 (versão do SDK, assinatura de métodos).

## Ciclo de cada fatia

1. **Plano**: `superpowers:writing-plans` com a fatia, os artefatos das fases 3 a 5 e as regras acima. O plano lista arquivos, testes e critérios de pronto.
2. **Isolamento** (opcional, recomendado): `superpowers:using-git-worktrees`.
3. **Execução**, escolher um dos dois caminhos e registrar no estado:
   - **Padrão:** `superpowers:subagent-driven-development` com `superpowers:test-driven-development` em cada tarefa. Ele já faz revisão de especificação e de qualidade por tarefa e uma revisão final da branch; por isso a revisão genérica do pr-review-toolkit não roda neste caminho.
   - **Alternativo:** `superpowers:executing-plans` com TDD; neste caminho, `/pr-review-toolkit:review-pr` é o revisor genérico da fatia.
   Para adapters de provider, usar o modo `adapter <provider>` de `ciclo-chatbot:providers-whatsapp`.
4. **Revisões especializadas em paralelo** (mesma mensagem, só o que o caminho escolhido não cobre):
   - agente `revisor-modularidade` deste plugin (duplicação com jscpd, fronteiras, responsabilidades), sempre;
   - agentes `silent-failure-hunter` e, em código tipado, `type-design-analyzer` do pr-review-toolkit;
   - `/pr-review-toolkit:review-pr` apenas no caminho alternativo.
   Corrigir achados com `superpowers:receiving-code-review` (avaliar tecnicamente, não aceitar às cegas).
5. **Verificação**: `superpowers:verification-before-completion`: rodar testes, lint, checagem de tipos e de fronteiras e mostrar a saída antes de dizer que terminou.
6. **Fechamento**: `/commit` (commit-commands) e `superpowers:finishing-a-development-branch`.
7. Atualizar `.ciclo-chatbot/estado.md` com a fatia concluída.

Se uma peça do superpowers ou do pr-review-toolkit não estiver instalada, seguir o mesmo ciclo manualmente e registrar no estado.

## Esqueleto primeiro (fatia 0)

Antes de qualquer IA: mensagem real do número de teste da Meta → túnel local → webhook com assinatura → `inbound_events` → fila → worker → resposta fixa pelo adapter → status `delivered`/`read` gravados. Isso testa as partes mais arriscadas (assinatura, idempotência, fila, envio) com o menor código possível. O usuário precisa de um app Meta de desenvolvimento com número de teste; guiar pelos passos iniciais de `ciclo-chatbot:conectar-whatsapp`.

## Portão da fase 6

Apresentar por fatia: o que entrou, testes, resultado dos revisores e saída da verificação. A fase 6 termina quando todas as fatias planejadas passaram pelo ciclo.
