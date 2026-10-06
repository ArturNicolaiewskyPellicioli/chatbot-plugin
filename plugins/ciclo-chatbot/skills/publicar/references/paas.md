# PaaS: comparação e receitas

Conferido em 2026-10-06. Preços e regiões mudam: conferir na página da plataforma no dia da decisão.

## Comparação para este workload (web + worker + Postgres/pgvector + Redis)

| | Railway | Render | Fly.io |
|---|---|---|---|
| Região no Brasil | não (US West, US East, EU West, Singapura) ([regiões](https://docs.railway.com/reference/deployment-regions)) | não (Oregon, Ohio, Virgínia, Frankfurt, Singapura) ([regiões](https://render.com/docs/regions)) | sim, `gru` (São Paulo), com Managed Postgres; preço em `gru` com multiplicador ([regiões](https://docs.fly.io/reference/regions), [preços](https://docs.fly.io/about/pricing/)) |
| Web + worker | serviços separados | tipo de serviço Background Worker ([docs](https://render.com/docs/background-workers)) | grupos de `[processes]` ([config](https://docs.fly.io/reference/configuration/)) |
| pgvector | a imagem padrão não inclui; usar o template de pgvector ([guia](https://docs.railway.com/guides/rag-pipeline-pgvector)) | suportado com `CREATE EXTENSION vector` ([extensões](https://render.com/docs/postgresql-extensions)) | incluído no Managed Postgres, com alta disponibilidade e PgBouncer ([mpg](https://fly.io/mpg/)) |
| Redis | template | Key Value (Valkey); `noeviction` para filas ([docs](https://render.com/docs/key-value)) | Upstash; usar plano fixo com BullMQ, porque o polling encarece o pague-pelo-uso ([docs](https://docs.fly.io/upstash/redis)) |
| Migração no deploy | `deploy.preDeployCommand`; falha interrompe o deploy ([docs](https://docs.railway.com/guides/pre-deploy-command)) | pre-deploy command, só em planos pagos; falha mantém a versão anterior ([docs](https://render.com/docs/deploys)) | `release_command` em máquina temporária; falha interrompe ([config](https://docs.fly.io/reference/configuration/)) |
| Cron | `cronSchedule`, mínimo de 5 min, UTC ([docs](https://docs.railway.com/reference/cron-jobs)) | cron jobs nativos | sem cron nativo; supercronic ou máquinas agendadas ([docs](https://fly.io/docs/blueprints/task-scheduling/)) |
| Ambientes de PR | automáticos ([docs](https://docs.railway.com/reference/environments)) | Preview Environments em workspace Pro com Blueprint ([docs](https://render.com/docs/preview-environments)) | action `superfly/fly-pr-review-apps` ([guia](https://fly.io/docs/blueprints/review-apps-guide/)) |
| Backups / PITR | snapshots de volume e PITR do Postgres na aba Backups ([backups](https://docs.railway.com/reference/backups), [PITR](https://docs.railway.com/volumes/point-in-time-recovery)) | PITR em bancos pagos (3 dias Hobby, 7 dias Pro+) ([docs](https://render.com/docs/postgresql-backups)) | backups por 10 dias; restauração para novo cluster ([mpg](https://fly.io/mpg/)) |
| Cuidado | — | serviço web gratuito dorme após 15 min: inviável para webhook ([free](https://render.com/docs/free)) | sinal padrão de parada é SIGINT com 5 s: configurar `kill_signal = "SIGTERM"` e `kill_timeout` maior ([config](https://docs.fly.io/reference/configuration/)) |

Região: o caminho crítico de cada resposta é Meta → servidor → API do LLM → Meta. Medir a latência a partir das regiões candidatas antes de escolher; São Paulo só ganha se o caminho medido for menor ou se houver exigência contratual de dados no Brasil (a LGPD regula transferência internacional, art. 33, mas não exige hospedagem no país).

## Ferramentas por plataforma

| Plataforma | Usar | Limites |
|---|---|---|
| Railway | plugin `railway` (skill `use-railway` + MCP hospedado) ou `railway mcp` da CLI ≥ 5.44.0 ([docs](https://docs.railway.com/reference/mcp-server)) | repositório do MCP antigo arquivado em 2026-05 |
| Render | plugin `render@claude-plugins-official` e MCP `https://mcp.render.com/mcp` ([docs](https://render.com/docs/mcp-server)) | o MCP não cria worker, não apaga, não escala; consultas ao Postgres são só leitura: usar `render.yaml` |
| Fly.io | CLI `fly`; MCP `fly mcp server` ([docs](https://fly.io/docs/flyctl/mcp-server/)) | MCP experimental e sem deploy: usar `fly deploy`; não expor o servidor MCP remotamente |

## Receitas mínimas

### Railway
- Serviços: `web`, `worker`, Postgres (template pgvector), Redis.
- `railway.json` do web: health check em `/health/ready`, `preDeployCommand` com a migração, `overlapSeconds` e `drainingSeconds` para a troca de versão ([teardown](https://docs.railway.com/guides/deployment-teardown), [healthchecks](https://docs.railway.com/reference/healthchecks)).
- Variáveis por ambiente com referências `${{Postgres.DATABASE_URL}}` ([variáveis](https://docs.railway.com/reference/variables)).
- Deploy pelo GitHub com "Wait for CI" ([docs](https://docs.railway.com/deployments/github-autodeploys)).

### Render
- `render.yaml` (Blueprint) com `web`, `worker`, Postgres e Key Value; `preDeployCommand` (plano pago); `healthCheckPath`.
- Desligamento: SIGTERM com espera padrão de 30 s, configurável até 300 s ([deploys](https://render.com/docs/deploys)).
- Deploy "After CI Checks Pass".

### Fly.io
- `fly.toml` com `[processes] web = "..."  worker = "..."`, `release_command` para migração, `kill_signal = "SIGTERM"`, `kill_timeout` ≥ maior job, `[[http_service.checks]]` esperando 200.
- Managed Postgres (`fly mpg`) e Upstash Redis em plano fixo.
- CI: `superfly/flyctl-actions/setup-flyctl` + `flyctl deploy --remote-only` com `FLY_API_TOKEN` de deploy ([docs](https://fly.io/docs/launch/continuous-deployment-with-github-actions/)).
