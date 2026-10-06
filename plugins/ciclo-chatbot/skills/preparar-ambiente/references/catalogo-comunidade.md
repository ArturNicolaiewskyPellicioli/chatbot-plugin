# Catálogo de peças da comunidade

Verificado em 2026-10-06. Nomes de plugins, skills e agentes foram lidos dos arquivos `marketplace.json`, `plugin.json` e `SKILL.md` de cada repositório. Estrelas e licenças vêm das páginas dos repositórios no GitHub (arredondadas). Antes de instalar, conferir se o repositório continua ativo; nomes podem mudar entre versões.

Critério de entrada: mantido por um fornecedor oficial ou com adoção ampla, licença clara e atividade recente. Peças com baixa adoção entram só como referência de leitura.

## Marketplaces

| Nome do marketplace | Repositório | Como adicionar |
|---|---|---|
| `claude-plugins-official` | anthropics/claude-plugins-official (Apache-2.0, ~37k ★) | já vem configurado |
| `claude-code-workflows` | wshobson/agents (MIT, ~40k ★) | `claude plugin marketplace add wshobson/agents` |
| `supabase-agent-skills` | supabase/agent-skills (MIT, ~2,4k ★) | `claude plugin marketplace add supabase/agent-skills` |
| `aiguide` | timescale/pg-aiguide (Apache-2.0, ~1,8k ★) | `claude plugin marketplace add timescale/pg-aiguide` |
| `anthropic-agent-skills` | anthropics/skills (Apache-2.0 nas skills de exemplo, ~178k ★) | `claude plugin marketplace add anthropics/skills` |
| `promptfoo` | promptfoo/promptfoo (MIT, ~24k ★) | `claude plugin marketplace add promptfoo/promptfoo` |
| `trailofbits` | trailofbits/skills (CC-BY-SA-4.0, ~7,3k ★) | `claude plugin marketplace add trailofbits/skills` |

Atenção à licença da Trail of Bits: CC-BY-SA exige compartilhamento pela mesma licença se o texto for copiado ou adaptado. Por isso o ciclo-chatbot só invoca essas skills; não copia o conteúdo delas.

## Camada `nucleo` (sempre)

| Plugin | Instalar | O que entra no ciclo |
|---|---|---|
| superpowers (obra/superpowers, MIT, ~294k ★) | `claude plugin install superpowers@claude-plugins-official` | `brainstorming`, `writing-plans`, `executing-plans`, `subagent-driven-development`, `dispatching-parallel-agents`, `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `requesting-code-review`, `receiving-code-review`, `using-git-worktrees`, `finishing-a-development-branch` |
| feature-dev | `claude plugin install feature-dev@claude-plugins-official` | `/feature-dev`, agentes `code-explorer`, `code-architect`, `code-reviewer` |
| pr-review-toolkit | `claude plugin install pr-review-toolkit@claude-plugins-official` | `/pr-review-toolkit:review-pr`, agentes `code-reviewer`, `code-simplifier`, `silent-failure-hunter`, `type-design-analyzer`, `pr-test-analyzer`, `comment-analyzer` |
| security-guidance | `claude plugin install security-guidance@claude-plugins-official` | hooks sempre ativos de segurança em edições e commits (requer Python 3.8+) |
| commit-commands | `claude plugin install commit-commands@claude-plugins-official` | `/commit`, `/commit-push-pr` |

O plugin opcional `ciclo-chatbot-essenciais`, no mesmo marketplace do ciclo-chatbot, instala esses cinco de uma vez como dependências.

## Camada `banco`

| Peça | Instalar | O que entra no ciclo |
|---|---|---|
| Supabase Postgres best practices | `claude plugin install postgres-best-practices@supabase-agent-skills` | **regras**: skill `supabase-postgres-best-practices`, 30 regras (índices, pooling, RLS, tipos, chaves, FKs, particionamento, locks, paginação, upsert, JSONB, busca textual). Vale para Postgres em qualquer hospedagem |
| pg-aiguide (TigerData) | `claude plugin install pg@aiguide` | **desenho, vetores e migrações**: skills `design-postgres-tables`, `pgvector-semantic-search`, `postgres-hybrid-text-search`, `postgres-database-migration`; MCP de busca na documentação do Postgres (não acessa seu banco) |
| wshobson database-design | `claude plugin install database-design@claude-code-workflows` | **segunda opinião**: só o agente `database-architect`, como revisor independente. A skill `postgresql-table-design` do mesmo plugin não é usada, para não triplicar a fonte de desenho de tabelas |

Uma peça principal por assunto: regras (Supabase), desenho de tabelas, pgvector e migrações (pg-aiguide), segurança de migração no dia a dia (`migracoes-seguras.md` deste plugin + Squawk). Os dois revisores independentes (`revisor-banco` e `database-architect`) são uma exceção deliberada à regra de não sobrepor: usam métodos diferentes (checklist com fontes e visão de escala) e não veem a revisão um do outro.
| Squawk (sbdchd/squawk, Apache-2.0/MIT, ~1,2k ★) | `npm i -g squawk-cli` ou `pip install squawk-cli` | lint de migrações SQL; o hook deste plugin roda automaticamente em arquivos de migração |
| Postgres MCP Pro (crystaldba/postgres-mcp, MIT, ~3,2k ★) | `claude mcp add --scope local postgres -e DATABASE_URI=postgresql://... -- uvx postgres-mcp --access-mode=restricted` | `analyze_db_health`, `explain_query` (com índices hipotéticos), `analyze_workload_indexes`, `get_top_queries`. Usar só em banco local, de staging ou réplica, com papel somente leitura. Ajuste de índices requer as extensões `pg_stat_statements` e `hypopg`. Última versão no PyPI é de 2025-05: conferir se segue mantido |

Opcionais conforme a stack ou hospedagem:
- Prisma: `npx skills add prisma/skills` (skills para Prisma 7). MCP local `npx -y prisma mcp`: negar a ferramenta `migrate-reset` nas permissões.
- Supabase hospedado: `claude plugin install supabase@claude-plugins-official` ou MCP `https://mcp.supabase.com/mcp?project_ref=<ref>&read_only=true`.
- Neon hospedado: `claude plugin install neon@claude-plugins-official`.
- Não encontramos skills oficiais de Drizzle, SQLAlchemy ou Alembic; usar Context7 para a documentação.

## Camada `ia`

| Peça | Instalar | O que entra no ciclo |
|---|---|---|
| claude-api (Anthropic) | `claude plugin install claude-api@anthropic-agent-skills` | modelos atuais, preços, tool use, structured outputs, prompt caching, Agent SDK, batches |
| llm-application-dev (wshobson) | `claude plugin install llm-application-dev@claude-code-workflows` | só as skills: `rag-implementation`, `hybrid-search-implementation`, `embedding-strategies`, `vector-index-tuning`, `prompt-engineering-patterns`, `llm-evaluation`. Os agentes do plugin (`ai-engineer`, `prompt-engineer`, `vector-database-engineer`) duplicam o `engenheiro-ia` e não são acionados. Algumas referências de modelos estão desatualizadas: conferir modelos e preços pela skill `claude-api` ou pela documentação |
| promptfoo | `claude plugin install promptfoo@promptfoo` | skills `promptfoo-evals`, `promptfoo-provider-setup`, `promptfoo-redteam-setup`, `promptfoo-redteam-run`. MCP opcional: `claude mcp add promptfoo -- npx promptfoo@latest mcp --transport stdio` |
| Langfuse docs (MCP) | já vem no `.mcp.json` deste plugin | documentação do Langfuse |
| Langfuse API (MCP) | `claude mcp add --scope local --transport http langfuse https://cloud.langfuse.com/api/public/mcp --header "Authorization: Basic <base64(pk:sk)>"` | prompts e traces do bot (usar o host da sua região) |

Alternativas por stack: Vercel AI SDK (`npx skills add vercel/ai --skill ai-sdk`), docs MCP do LangChain/LangGraph (`https://docs.langchain.com/mcp`), docs MCP do Mastra (`npx -y @mastra/mcp-docs-server@latest`), DeepEval (`deepeval@claude-plugins-official`) como alternativa Python ao promptfoo. Instalar só a que corresponde ao ADR de IA.

## Camadas `stack-ts` e `stack-python`

| Stack | Instalar |
|---|---|
| TypeScript | `typescript-lsp@claude-plugins-official`; `javascript-typescript@claude-code-workflows` (skill `nodejs-backend-patterns`) |
| Python | `pyright-lsp@claude-plugins-official`; `python-development@claude-code-workflows` (agente `fastapi-pro`) |
| Ambas | `backend-development@claude-code-workflows` (skills `api-design-principles`, `architecture-patterns`); `c4-architecture@claude-code-workflows` (`/c4-architecture`) |
| Duplicação | `npm i -g jscpd` (detector de código duplicado, várias linguagens) |

## Camada `whatsapp`

Não existe MCP oficial da Meta para a WhatsApp Cloud API (verificado em 2026-10-06). O desenho dos adapters é do próprio ciclo-chatbot.

| Situação | Instalar |
|---|---|
| Adapter Twilio | `claude plugin install twilio-developer-kit@claude-plugins-official` (skills `twilio-whatsapp-send-message`, `twilio-messaging-webhooks`, `twilio-webhook-architecture`, `twilio-security-api-auth`, `twilio-reliability-patterns`, `twilio-content-template-builder`) |
| Adapter 360dialog | MCP oficial hospedado `https://mcp.360dialog.com/mcp` (canais, templates, webhooks, saldo) |
| Túnel para webhook local | `cloudflared tunnel --url http://localhost:<porta>` ou ngrok |

Não usar `lharries/whatsapp-mcp`: ele conecta uma conta pessoal via whatsmeow e não serve para bot de empresa. Skills comunitárias de Cloud API encontradas têm adoção muito baixa (1 a 10 ★): servem só como leitura.

## Camada `seguranca`

| Peça | Instalar |
|---|---|
| claude-security | `claude plugin install claude-security@claude-plugins-official` (`/claude-security`, varredura com relatórios SARIF) |
| Trail of Bits | `claude plugin install insecure-defaults@trailofbits`, `supply-chain-risk-auditor@trailofbits`, `sharp-edges@trailofbits` |
| Opcional | `property-based-testing@trailofbits` para parsers de webhook |

Fora: `semgrep/mcp` foi arquivado (o servidor passou para o binário `semgrep` e o plugin `semgrep`).

## Camadas de deploy

| PaaS | Instalar | Limites conhecidos |
|---|---|---|
| Railway | `claude plugin install railway@claude-plugins-official` (skill `use-railway`, MCP hospedado com OAuth) ou `railway mcp install --agent claude-code` | o repositório `railwayapp/railway-mcp-server` foi arquivado em 2026-05; usar o plugin ou a CLI (≥ 5.44.0) |
| Render | `claude plugin install render@claude-plugins-official`; MCP `https://mcp.render.com/mcp` | o MCP não cria background workers, não apaga e não escala: usar Blueprint (`render.yaml`) para o worker |
| Fly.io | `claude mcp add flyctl -- fly mcp server` | MCP experimental e sem deploy: usar `fly deploy` |

## Camada `observabilidade`

| Peça | Instalar |
|---|---|
| Sentry | `claude mcp add --scope local --transport http sentry https://mcp.sentry.dev/mcp` (OAuth) |
| CI | `claude plugin install cicd-automation@claude-code-workflows` (skill `github-actions-templates`) |
| Monitoramento | `observability-monitoring@claude-code-workflows`, `incident-response@claude-code-workflows` |
| GitHub | `claude mcp add --transport http github https://api.githubcopilot.com/mcp -H "Authorization: Bearer $GITHUB_PAT"` |

## Testes de carga

- k6 (CLI da Grafana) é suficiente. O `grafana/mcp-k6` é experimental e AGPL-3.0: opcional.

## Fora do catálogo, e por quê

| Peça | Motivo |
|---|---|
| Cópias de plugins dentro de `anthropics/claude-code` | versões antigas; usar o marketplace oficial |
| `code-review` + `pr-review-toolkit` + `code-simplifier` juntos | sobreposição |
| `database-migrations` (wshobson) | sobrepõe `pg:postgres-database-migration` e `migracoes-seguras.md` |
| Agentes do `llm-application-dev` | sobrepõem o `engenheiro-ia`; as skills do plugin são usadas |
| `automazeio/ccpm` | sem atividade há mais de 6 meses |
| Listas `awesome-*` sem licença | servem para descobrir, não para copiar |
| `Meta WhatsApp-Nodejs-SDK` | arquivado pela Meta |
