---
name: operar
description: Opera o chatbot de WhatsApp com IA depois do go-live, com painéis e alertas, ciclo semanal de melhoria a partir de conversas reais (falhas viram casos de eval), revisão mensal de custos (LLM e mensagens da Meta), qualidade do número, templates, retenção e LGPD, atualizações de versão da Graph API e de dependências, e runbook de incidentes. Usar quando o usuário disser "operar o bot", "o bot está caro", "o bot errou", "revisão semanal", "incidente", "runbook", "atualizar versão da API", ou na fase 11 do /ciclo-chatbot:iniciar.
argument-hint: "[semanal | mensal | incidente <descrição> | custos]"
---

# Operação

Runbook e rotinas em `${CLAUDE_SKILL_DIR}/references/runbook.md`. Na primeira execução, gerar `docs/chatbot/11-runbook.md` a partir dele, preenchido com as URLs, painéis e contatos reais do projeto.

## Modos

- `semanal`: amostrar conversas da semana (Langfuse), classificar falhas, transformar as relevantes em casos de eval, propor ajustes de prompt ou base de conhecimento por PR, que só entra com as evals passando (fase 7).
- `mensal`: custos por conversa e por tenant (LLM + Meta), qualidade do número e faixa de limite, templates pausados, versões (Graph API, SDKs, pgvector, Postgres), dependências com vulnerabilidade, retenção executada, pedidos de titulares atendidos.
- `incidente`: seguir o roteiro do runbook para o sintoma; usar `superpowers:systematic-debugging` para achar a causa; registrar linha do tempo e correção; se houver dado pessoal envolvido, avaliar comunicação à ANPD (LGPD art. 48).
- `custos`: quebrar o custo por etapa do pipeline (`llm_runs.purpose`), medir taxa de acerto do cache e testar troca de modelo por papel com as evals antes de mudar.

Ferramentas: MCP do Sentry (erros), MCP do Langfuse (traces e prompts), MCP ou CLI do PaaS (logs e deploys), Postgres MCP Pro em réplica ou staging, nunca escrevendo em produção.
