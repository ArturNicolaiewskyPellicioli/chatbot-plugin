---
name: publicar
description: Publica o chatbot em PaaS (Railway, Render ou Fly.io) com staging e produção, Postgres com pgvector, Redis, processos web e worker, migrações no pré-deploy, health checks, desligamento gracioso, CI/CD no GitHub Actions, segredos por ambiente, backups com PITR, observabilidade (logs, OpenTelemetry, Sentry, Langfuse) e rollback ensaiado, usando os plugins e MCPs oficiais de cada plataforma. Usar quando o usuário disser "publicar o bot", "fazer deploy", "subir para produção", "configurar CI/CD", "Railway", "Render", "Fly.io", ou na fase 9 do /ciclo-chatbot:iniciar.
argument-hint: "[staging | producao | ci | observabilidade | rollback]"
---

# Publicação

Entrada: ADR 0005 (PaaS, região, ambientes) e ADR 0007 (observabilidade). Material de apoio em `${CLAUDE_SKILL_DIR}/references/`:
- `paas.md`: comparação e receitas por plataforma (Railway, Render, Fly.io), com limites conhecidos das ferramentas
- `ci-observabilidade.md`: pipeline do GitHub Actions, health checks, desligamento gracioso, logs, traces, erros, alertas

## Passos

1. **Ferramentas da plataforma**: rodar `ciclo-chatbot:preparar-ambiente` com a camada do PaaS escolhido (`deploy-railway`, `deploy-render` ou `deploy-fly`) e `observabilidade`. Usar a skill e o MCP da plataforma quando existirem; quando a ferramenta não cobrir algo (worker no MCP da Render, deploy no MCP do Fly), usar a CLI ou o arquivo de configuração como descrito em `paas.md`. Pedir ao usuário que faça login nas CLIs; nunca pedir senha no chat.
2. **Infraestrutura como código**: disparar o agente `engenheiro-deploy` deste plugin com os ADRs e os caminhos de `paas.md` e `ci-observabilidade.md`, para gerar o arquivo de configuração da plataforma (`railway.json`/`railway.toml`, `render.yaml`, `fly.toml`) com web, worker, Postgres com pgvector, Redis, health checks, comando de pré-deploy para migrações e sinais de desligamento. Build pelo builder nativo da plataforma; Dockerfile multi-stage só se houver dependência de sistema (ex.: ffmpeg para áudio).
3. **Ambientes**: staging e produção separados, cada um com seu banco, Redis, segredos e número de WhatsApp (staging usa o número de teste da Meta).
4. **CI/CD**: pipeline de `ci-observabilidade.md`. Se o plugin `cicd-automation` estiver instalado, usar a skill `github-actions-templates` como base. Deploy em staging automático após o CI; produção com aprovação manual (GitHub Environments).
5. **Observabilidade**: logs JSON, OpenTelemetry, Sentry para erros e uptime, Langfuse para traces de LLM com identificadores em hash.
6. **Dados**: ativar backups e PITR do Postgres gerenciado; fazer uma restauração de teste em um banco novo e registrar o tempo.
7. **Deploy em staging** → teste de fumaça com o número de teste (fatia 0 ponta a ponta) → evals contra staging.
8. **Rollback**: ensaiar a volta para a versão anterior em staging e registrar o passo a passo no runbook.
9. **Produção**: deploy com aprovação. A conexão do número real é a fase 10.
10. Rodar o checklist da fase 9 e apresentar o portão com URLs de staging e produção, resultado do teste de fumaça, tempo de restauração e passo a passo do rollback.
