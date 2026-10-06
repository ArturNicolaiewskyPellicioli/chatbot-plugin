# Runbook de operação

## Painel mínimo

| Métrica | Fonte |
|---|---|
| Mensagens recebidas por minuto, por número | `inbound_events` / logs |
| Tempo até o 200 no webhook (p50, p99) | traces |
| Atraso da fila e tempo de resposta ao contato (p50, p95) | traces / `llm_runs.latency_ms` |
| Erros de envio por tipo (`NormalizedError`) | logs |
| Status `failed` por código | `message_status_events` |
| Taxa de transbordo e de resolução sem humano | `handoffs`, `conversations` |
| Nota das evals em amostra de produção | Langfuse |
| Custo por conversa (LLM + Meta) e por tenant | `llm_runs.cost_usd`, status com `billable` |
| Taxa de acerto do cache de prompt | `llm_runs.cache_read_tokens` |
| Qualidade do número e faixa de limite | painel da Meta / API |

## Roteiros por sintoma

| Sintoma | Verificar | Ação |
|---|---|---|
| Webhook devolvendo não-200 | logs do web, assinatura, banco | corrigir e publicar; a Meta reenvia por até 7 dias e a inbox deduplica, então não reprocessar à mão |
| Bot não responde, webhook OK | atraso da fila, worker vivo, erros de LLM | escalar worker; se o LLM estiver fora, ativar modelo reserva ou mensagem de espera + transbordo |
| Erro `Auth` no envio | token do usuário do sistema | gerar novo token, atualizar o segredo, reiniciar |
| Muitos 130429 | vazão por número | reduzir paralelismo; conferir se o limitador está ativo |
| Muitos 131056 | mensagens seguidas ao mesmo contato | juntar respostas em uma mensagem; respeitar 6 s por destinatário |
| Qualidade YELLOW/RED | templates e mensagens proativas recentes, bloqueios | pausar campanhas, revisar opt-in e conteúdo |
| Template PAUSED | qualidade do template | trocar texto, reenviar para aprovação, usar alternativo |
| Custo subiu | `llm_runs` por `purpose`, cache, mensagens por conversa | ver modo `custos` |
| Resposta errada ou perigosa | trace da conversa | caso de eval + correção por PR; transbordo manual se urgente |
| Provider fora do ar | status do provider | política da fase 5: nunca failover silencioso para outro número |

## Rotinas

- Semanal: ciclo de evals com conversas reais; templates pausados; erros novos no Sentry.
- Mensal: custos; versões; dependências; retenção (partições antigas removidas, payloads brutos apagados); pedidos de titulares.
- Trimestral: ensaio de restauração de backup; ensaio de rollback; rotação de segredos; revisão do red team.
- A cada nova versão da Graph API: ler o changelog, testar em staging com os testes de contrato, atualizar a configuração. Cada versão vale cerca de dois anos ([versões](https://developers.facebook.com/docs/graph-api/changelog/versions/)).
