# CI/CD e observabilidade

## Pipeline do GitHub Actions

```
pull_request / push:
  1. instalar dependências (cache)
  2. lint + checagem de tipos
  3. fronteiras entre módulos (dependency-cruiser / import-linter) + jscpd
  4. testes unitários e de contrato
  5. testes de integração com serviço pgvector/pgvector + redis
  6. squawk nas migrações novas (sbdchd/squawk-action)
  7. evals de regressão (promptfoo/promptfoo-action) com meta mínima
  8. auditoria de dependências
push na main (após 1–8):
  9. deploy em staging (automático) → teste de fumaça
 10. deploy em produção (GitHub Environment com aprovação)
```

- Segredos por ambiente em GitHub Environments; revisores obrigatórios em repositório privado exigem plano Pro, Team ou Enterprise ([docs](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)).
- Evals custam tokens: rodar a suíte de regressão em todo PR que toca `prompts/`, `src/modules/ai/` ou `src/modules/knowledge/`, e a completa antes de release.

## Processos e sinais

- Migração só no comando de pré-deploy, como processo administrativo único ([12factor XII](https://12factor.net/admin-processes)).
- `CMD` em forma exec para o sinal chegar ao processo ([Docker](https://docs.docker.com/build/building/best-practices/)).
- Worker BullMQ: `await worker.close()` em SIGTERM e SIGINT; Redis com `noeviction` e AOF ([BullMQ](https://docs.bullmq.io/guide/going-to-production)). Celery: warm shutdown no SIGTERM e `acks_late` ([Celery](https://docs.celeryq.dev/en/stable/userguide/workers.html)).
- Janela de drenagem da plataforma maior que o job mais longo (chamada de LLM + envio).

## Health checks

- `/health/live`: o processo responde (sem dependências).
- `/health/ready`: banco e Redis acessíveis; usado pela plataforma para liberar tráfego.
- Nenhum detalhe interno na resposta.

## Observabilidade

| Sinal | Como | Fonte |
|---|---|---|
| Logs | JSON em stdout, um evento por linha, com `trace_id`, `tenant_id`, `conversation_id`; telefone em hash | [12factor XI](https://12factor.net/logs) |
| Traces | OpenTelemetry; em Node, sem mudar código: `NODE_OPTIONS="--require @opentelemetry/auto-instrumentations-node/register"` + `OTEL_SERVICE_NAME` + `OTEL_EXPORTER_OTLP_ENDPOINT` | [OTel JS zero-code](https://opentelemetry.io/docs/zero-code/js/) |
| Convenções de IA | atributos `gen_ai.*` (operação, provider, tokens de entrada, saída e cache, conversa); especificação ainda em desenvolvimento | [semconv GenAI](https://github.com/open-telemetry/semantic-conventions-genai) |
| Traces de LLM | Langfuse (SDK baseado em OTel; aceita OTLP em `/api/public/otel`); `session.id` = conversa, `user.id` = hash do contato | [Langfuse OTel](https://langfuse.com/docs/opentelemetry/get-started), [sessões](https://langfuse.com/docs/observability/features/sessions) |
| Custos | enviar uso de tokens ao Langfuse (tem prioridade sobre o custo inferido) + custo de mensagens da Meta a partir dos status | [Langfuse custos](https://langfuse.com/docs/observability/features/token-and-cost-tracking) |
| Erros | Sentry, convivendo com o pipeline OTel | [Sentry + OTel](https://docs.sentry.io/platforms/javascript/guides/node/opentelemetry/) |
| Uptime | Sentry Uptime (1 min a 1 h; alerta após 3 falhas seguidas por padrão) ou Better Stack | [Sentry Uptime](https://docs.sentry.io/product/uptime-monitoring/) |

## Alertas mínimos

- Webhook: taxa de não-200 > 0 por 5 min (a Meta vai reenviar, mas é sinal de problema).
- Fila: atraso acima do orçamento de latência.
- Erros 130429 / 131056 (vazão) e `Auth` (token) no envio.
- Status `failed` acima do normal.
- Custo diário de LLM e de mensagens acima do teto.
- Qualidade do número mudou para YELLOW ou RED; template PAUSED.
