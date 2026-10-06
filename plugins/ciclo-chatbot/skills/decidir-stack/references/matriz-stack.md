# Matriz de decisão de stack

Dar peso de 1 a 5 a cada critério com o usuário; notas de 1 a 5 por opção, com uma linha de justificativa e a fonte. Conferir versões com Context7 na data da decisão.

## Critérios sugeridos

| Critério | O que medir |
|---|---|
| Experiência do time | anos de uso, código existente para reaproveitar |
| Ecossistema de IA | SDK oficial do provider de LLM, structured outputs, streaming |
| Ecossistema WhatsApp | SDK maduro ou facilidade de cliente HTTP próprio |
| ORM e migrações | migrações SQL revisáveis, suporte a SQL bruto (particionamento, pgvector, RLS), geração de tipos |
| Fila e worker | maturidade, retentativas, desligamento gracioso |
| Tipagem e manutenção | tipos de ponta a ponta, refatoração segura |
| Deploy no PaaS | suporte nativo do builder, imagem pequena |
| Custo de operação | memória por processo, cold start, preço |

## Opções conhecidas (conferir estado atual)

### TypeScript
- Web: NestJS (módulos e injeção de dependência ajudam a manter fronteiras) ou Fastify/Hono (mais enxutos).
- ORM: Prisma 7 (migrações SQL geradas e editáveis; skills oficiais em `prisma/skills`), Drizzle (SQL-first, migrações SQL), Kysely (query builder tipado).
- Fila: BullMQ (Redis). Produção: `maxRetriesPerRequest: null`, Redis com `noeviction` e AOF, `worker.close()` no SIGTERM ([BullMQ: going to production](https://docs.bullmq.io/guide/going-to-production)).
- LLM: SDK oficial do provider; Vercel AI SDK se precisar trocar de provider com frequência; Claude Agent SDK se o bot precisar de um agente com ferramentas complexas.
- WhatsApp: cliente HTTP próprio dentro do adapter, ou `whatsapp-api-js` / `@great-detail/whatsapp` (MIT). O SDK Node oficial da Meta está arquivado ([repo](https://github.com/WhatsApp/WhatsApp-Nodejs-SDK)).
- Fronteiras: `dependency-cruiser` ou `eslint-plugin-boundaries` para impedir importação proibida entre módulos.

### Python
- Web: FastAPI.
- ORM: SQLAlchemy 2 + Alembic (`CREATE INDEX CONCURRENTLY` dentro de `autocommit_block()`, ver [Alembic](https://alembic.sqlalchemy.org/en/latest/api/runtime.html)).
- Fila: Celery (SIGTERM faz warm shutdown; `acks_late` evita perder tarefa em andamento, ver [Celery workers](https://docs.celeryq.dev/en/stable/userguide/workers.html)), arq ou Dramatiq.
- LLM: SDK oficial do provider; Pydantic AI ou LangGraph só com ganho concreto.
- WhatsApp: `pywa` (MIT, valida assinatura, integra com FastAPI) ou cliente HTTP próprio.
- Fronteiras: `import-linter`.

## Formato de ADR

```markdown
# NNNN. <Título da decisão>

Data: AAAA-MM-DD · Status: proposto | aceito | substituído por NNNN

## Contexto
<requisitos e restrições que forçam a decisão, com números da descoberta>

## Opções consideradas
1. <opção> — prós, contras, fonte
2. <opção> — prós, contras, fonte

## Decisão
<opção escolhida e por quê>

## Consequências
<o que fica mais fácil, o que fica mais difícil, o que precisa ser revisto e quando>
```
