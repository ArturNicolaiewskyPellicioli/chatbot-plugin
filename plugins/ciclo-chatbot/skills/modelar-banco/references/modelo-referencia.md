# Modelo de dados de referência: chatbot com IA multi-provider

Ponto de partida, não receita. Ajustar à descoberta: remover o que o projeto não usa e justificar no documento da fase o que for acrescentado. DDL para PostgreSQL 18 (`uuidv7()` nativo). Em PostgreSQL 16 ou 17, gerar UUIDv7 na aplicação ou trocar o default.

Validado em 2026-10-06 em PostgreSQL 18.6 com pgvector 0.8.7: o DDL aplica sem erro e passa sem alertas no Squawk 2.67 com o `.squawk.toml` de `migracoes-seguras.md`; FKs compostas recusam referência entre tenants; RLS falha fechado inclusive em conexão reaproveitada; o job de eliminação roda na ordem documentada sem erro de FK; `DETACH PARTITION ... CONCURRENTLY` funciona. Num teste de volume com 2 milhões de mensagens sintéticas e os mesmos índices, linha do tempo, atualização de status com janela e fila do outbox usaram os índices previstos.

## Decisões embutidas e por quê

| Decisão | Motivo | Fonte |
|---|---|---|
| Chaves `uuid` v7 nas entidades | ordenadas no tempo, com melhor localidade de índice que UUIDv4; podem ser geradas fora do banco | [RFC 9562](https://www.rfc-editor.org/rfc/rfc9562.html), [PG: funções UUID](https://www.postgresql.org/docs/current/functions-uuid.html) |
| `bigint` identity em tabelas internas (outbox, eventos) | metade do tamanho; nunca expostas | [PG wiki: Don't Do This](https://wiki.postgresql.org/wiki/Don%27t_Do_This) |
| `timestamptz`, `text`, identity; nada de `serial`, `varchar(n)`, `money` | recomendações da comunidade Postgres | [PG wiki: Don't Do This](https://wiki.postgresql.org/wiki/Don%27t_Do_This) |
| `tenant_id` em todas as tabelas de negócio + FKs compostas `(tenant_id, x)` | o banco recusa uma conversa do tenant B apontando para um contato do tenant A | [PG: constraints](https://www.postgresql.org/docs/current/ddl-constraints.html) |
| Contato por número da empresa, com telefone **ou** BSUID | o webhook pode vir sem telefone quando o usuário adota username; o BSUID tem escopo de portfólio | [Meta: BSUID](https://developers.facebook.com/documentation/business-messaging/whatsapp/business-scoped-user-ids/) |
| Janela de 24h em `contact_channels.last_inbound_at` | a janela é por número da empresa e usuário, não por conversa | [Meta: enviar mensagens](https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/send-messages) |
| Inbox idempotente (`inbound_events`) fora das tabelas particionadas | a Meta reenvia webhooks por até 7 dias e pode duplicar; em tabela particionada, a unique precisa incluir a chave de partição | [Meta: webhooks](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/overview), [PG: particionamento](https://www.postgresql.org/docs/current/ddl-partitioning.html) |
| Status de mensagem só avança | `delivered` pode não chegar depois de `read` | [Meta: status](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages/status/) |
| Outbox transacional | evento gravado na mesma transação da mudança; consumidor idempotente | [microservices.io](https://microservices.io/patterns/data/transactional-outbox.html) |
| `halfvec` + HNSW | metade do armazenamento; índice HNSW suporta até 4.000 dimensões em `halfvec` | [pgvector](https://github.com/pgvector/pgvector) |
| Sem partição `DEFAULT` | com partição default, `DETACH PARTITION ... CONCURRENTLY` é recusado; inserção fora das faixas falha alto e o evento continua na inbox para reprocessar | [PG: ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html) |
| Credenciais fora do banco | `credentials_ref` aponta para o cofre de segredos do PaaS | [12factor III](https://12factor.net/config) |
| FKs sem `CASCADE` nos dados de conversa | apagar em cascata através de partições é perigoso; a eliminação (LGPD) é um job explícito e ordenado | ver seção LGPD |

## DDL

```sql
-- Contadores (tokens por execução, tentativas, ordem do chunk) ficam em int de propósito:
-- não chegam perto do limite. Chaves usam uuid ou bigint.
-- squawk-ignore-file prefer-bigint-over-int
SET lock_timeout = '5s';
SET statement_timeout = '60s';

CREATE EXTENSION IF NOT EXISTS vector;

-- Tenants e contas de canal ----------------------------------------------
CREATE TABLE tenants (
  id          uuid PRIMARY KEY DEFAULT uuidv7(),
  name        text NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE channel_accounts (
  id                     uuid PRIMARY KEY DEFAULT uuidv7(),
  tenant_id              uuid NOT NULL REFERENCES tenants(id),
  provider               text NOT NULL CHECK (provider IN ('meta','360dialog','gupshup','twilio','evolution','zapi')),
  provider_app_ref       text NOT NULL,        -- app ou conta do provider que assina os webhooks (Meta: o app)
  external_account_id    text NOT NULL,        -- phone_number_id na Meta; instância na Evolution
  business_portfolio_id  text,                 -- escopo do BSUID na Meta
  display_phone          text,
  role                   text NOT NULL DEFAULT 'primary' CHECK (role IN ('primary','secondary','test')),
  is_official            boolean NOT NULL,     -- false para conexões via WhatsApp Web (Baileys, Z-API)
  credentials_ref        text NOT NULL,        -- nome do segredo no cofre; nunca o token
  status                 text NOT NULL DEFAULT 'active' CHECK (status IN ('active','paused','disabled')),
  created_at             timestamptz NOT NULL DEFAULT now(),
  UNIQUE (provider, external_account_id),
  UNIQUE (tenant_id, id)                       -- alvo das FKs compostas; também indexa tenant_id
);

-- Contatos ----------------------------------------------------------------
CREATE TABLE contacts (
  id            uuid PRIMARY KEY DEFAULT uuidv7(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id),
  display_name  text,
  created_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, id)
);

-- Presença de um contato num número da empresa (identidade + janela de 24h)
CREATE TABLE contact_channels (
  id                  uuid PRIMARY KEY DEFAULT uuidv7(),
  tenant_id           uuid NOT NULL,
  contact_id          uuid NOT NULL,
  channel_account_id  uuid NOT NULL,
  phone_e164          text,
  bsuid               text,
  username            text,
  last_inbound_at     timestamptz,
  CHECK (phone_e164 IS NOT NULL OR bsuid IS NOT NULL),
  UNIQUE (tenant_id, id),
  FOREIGN KEY (tenant_id, contact_id) REFERENCES contacts (tenant_id, id),
  FOREIGN KEY (tenant_id, channel_account_id) REFERENCES channel_accounts (tenant_id, id)
);
CREATE UNIQUE INDEX contact_channels_phone_uq ON contact_channels (channel_account_id, phone_e164) WHERE phone_e164 IS NOT NULL;
CREATE UNIQUE INDEX contact_channels_bsuid_uq ON contact_channels (channel_account_id, bsuid) WHERE bsuid IS NOT NULL;
CREATE INDEX contact_channels_account_idx ON contact_channels (channel_account_id);
CREATE INDEX contact_channels_contact_idx ON contact_channels (contact_id);
-- Reaproveitar o mesmo contato em outro número do mesmo portfólio (BSUID tem escopo de portfólio)
CREATE INDEX contact_channels_bsuid_tenant_idx ON contact_channels (tenant_id, bsuid) WHERE bsuid IS NOT NULL;

-- Consentimentos: só inserção, nunca update (histórico é a prova)
CREATE TABLE contact_consents (
  id           uuid PRIMARY KEY DEFAULT uuidv7(),
  tenant_id    uuid NOT NULL,
  contact_id   uuid NOT NULL,
  purpose      text NOT NULL,                  -- ex.: atendimento, marketing, lembretes
  status       text NOT NULL CHECK (status IN ('granted','revoked')),
  source       text NOT NULL,                  -- onde e como foi coletado
  evidence     jsonb,
  recorded_at  timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (tenant_id, contact_id) REFERENCES contacts (tenant_id, id)
);
CREATE INDEX contact_consents_lookup_idx ON contact_consents (contact_id, purpose, recorded_at DESC);

-- Fatos duráveis do contato (memória longa, mínima)
CREATE TABLE contact_facts (
  id                 uuid PRIMARY KEY DEFAULT uuidv7(),
  tenant_id          uuid NOT NULL,
  contact_id         uuid NOT NULL,
  key                text NOT NULL,
  value              text NOT NULL,
  source_message_id  uuid,
  updated_at         timestamptz NOT NULL DEFAULT now(),
  UNIQUE (contact_id, key),
  FOREIGN KEY (tenant_id, contact_id) REFERENCES contacts (tenant_id, id)
);

-- Conversas ---------------------------------------------------------------
CREATE TABLE conversations (
  id                  uuid PRIMARY KEY DEFAULT uuidv7(),
  tenant_id           uuid NOT NULL,
  contact_channel_id  uuid NOT NULL,
  status              text NOT NULL DEFAULT 'bot' CHECK (status IN ('bot','handoff','closed')),
  summary             text,                    -- resumo rolante para a memória do LLM
  summary_upto        timestamptz,             -- até qual mensagem o resumo cobre
  opened_at           timestamptz NOT NULL DEFAULT now(),
  last_activity_at    timestamptz NOT NULL DEFAULT now(),
  closed_at           timestamptz,
  UNIQUE (tenant_id, id),
  FOREIGN KEY (tenant_id, contact_channel_id) REFERENCES contact_channels (tenant_id, id)
);
CREATE UNIQUE INDEX conversations_one_open_uq ON conversations (contact_channel_id) WHERE status <> 'closed';
CREATE INDEX conversations_contact_channel_idx ON conversations (contact_channel_id);
CREATE INDEX conversations_inbox_idx ON conversations (tenant_id, status, last_activity_at DESC);

-- Inbox idempotente: todo webhook passa por aqui antes da fila -------------
-- Tabela de sistema: sem RLS (o tenant ainda não é conhecido na entrada); acesso só
-- pelos papéis de ingestão e worker; retenção curta.
CREATE TABLE inbound_events (
  provider            text NOT NULL,
  provider_event_id   text NOT NULL,           -- wamid para mensagens; wamid || ':' || status para status
  channel_account_id  uuid NOT NULL REFERENCES channel_accounts(id),
  kind                text NOT NULL CHECK (kind IN ('message','status','other')),
  payload             jsonb NOT NULL,          -- bruto, para reprocessar e depurar
  received_at         timestamptz NOT NULL DEFAULT now(),
  processed_at        timestamptz,
  attempts            int NOT NULL DEFAULT 0,
  last_error          text,
  PRIMARY KEY (provider, provider_event_id)
);
CREATE INDEX inbound_events_pending_idx ON inbound_events (received_at) WHERE processed_at IS NULL;
CREATE INDEX inbound_events_account_idx ON inbound_events (channel_account_id);
CREATE INDEX inbound_events_received_brin ON inbound_events USING brin (received_at);
-- Gravação no webhook: INSERT ... ON CONFLICT (provider, provider_event_id) DO NOTHING
-- Retenção: apagar em lotes o que tem received_at além de 14 dias (a Meta reenvia por até 7).

-- Mensagens (particionada por mês, sem partição DEFAULT) --------------------
CREATE TABLE messages (
  id                            uuid NOT NULL DEFAULT uuidv7(),
  tenant_id                     uuid NOT NULL,
  conversation_id               uuid NOT NULL,
  direction                     text NOT NULL CHECK (direction IN ('inbound','outbound')),
  author                        text NOT NULL CHECK (author IN ('contact','bot','agent','system')),
  provider                      text NOT NULL,
  provider_message_id           text,          -- nulo até o provider confirmar o envio
  type                          text NOT NULL, -- text, image, audio, document, interactive_reply, template, ...
  body                          text,
  media_object_key              text,          -- mídia copiada para storage próprio (URL da Meta expira em 5 min)
  reply_to_provider_message_id  text,
  status                        text NOT NULL DEFAULT 'received'
                                CHECK (status IN ('received','queued','sent','delivered','read','played','failed')),
  llm_run_id                    uuid,
  created_at                    timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (id, created_at),
  FOREIGN KEY (tenant_id, conversation_id) REFERENCES conversations (tenant_id, id)
) PARTITION BY RANGE (created_at);
CREATE INDEX messages_timeline_idx ON messages (conversation_id, created_at DESC);
CREATE INDEX messages_provider_id_idx ON messages (provider, provider_message_id) WHERE provider_message_id IS NOT NULL;
-- Linha do tempo: incluir created_at >= conversations.opened_at; sem esse limite,
-- a consulta faz uma busca de índice em cada partição.

-- Eventos de status (só inserção, particionada por mês). Tabela de sistema, como a inbox.
CREATE TABLE message_status_events (
  id                   bigint GENERATED ALWAYS AS IDENTITY,
  provider             text NOT NULL,
  provider_message_id  text NOT NULL,
  status               text NOT NULL CHECK (status IN ('sent','delivered','read','played','failed')),
  error_code           text,
  billable             boolean,
  pricing_category     text,
  occurred_at          timestamptz NOT NULL,
  received_at          timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (id, received_at)
) PARTITION BY RANGE (received_at);
CREATE INDEX message_status_events_msg_idx ON message_status_events (provider, provider_message_id);

-- Execuções de LLM e ferramentas ------------------------------------------
CREATE TABLE llm_runs (
  id                  uuid NOT NULL DEFAULT uuidv7(),
  tenant_id           uuid NOT NULL,
  conversation_id     uuid,                    -- nulo para embed e juiz de eval
  purpose             text NOT NULL,           -- guard, router, reply, summarize, embed, judge
  provider            text NOT NULL,
  model               text NOT NULL,
  prompt_version      text NOT NULL,
  input_tokens        int,
  output_tokens       int,
  cache_read_tokens   int,
  cache_write_tokens  int,
  cost_usd            numeric(12,6),
  latency_ms          int,
  status              text NOT NULL CHECK (status IN ('ok','error','refused','fallback')),
  trace_id            text,                    -- id do trace no Langfuse / OpenTelemetry
  created_at          timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (id, created_at),
  FOREIGN KEY (tenant_id, conversation_id) REFERENCES conversations (tenant_id, id)
) PARTITION BY RANGE (created_at);
CREATE INDEX llm_runs_conversation_idx ON llm_runs (conversation_id, created_at DESC);
CREATE INDEX llm_runs_tenant_created_idx ON llm_runs (tenant_id, created_at);

CREATE TABLE tool_calls (
  id               uuid PRIMARY KEY DEFAULT uuidv7(),
  tenant_id        uuid NOT NULL REFERENCES tenants(id),
  llm_run_id       uuid NOT NULL,              -- sem FK: llm_runs é particionada com PK (id, created_at)
  tool_name        text NOT NULL,
  args             jsonb NOT NULL,
  result           jsonb,
  status           text NOT NULL CHECK (status IN ('ok','error','denied','pending_approval')),
  idempotency_key  text UNIQUE,                -- efeitos colaterais externos
  created_at       timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX tool_calls_run_idx ON tool_calls (llm_run_id);
CREATE INDEX tool_calls_tenant_created_idx ON tool_calls (tenant_id, created_at);

-- Base de conhecimento ----------------------------------------------------
CREATE TABLE kb_documents (
  id            uuid PRIMARY KEY DEFAULT uuidv7(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id),
  source_uri    text NOT NULL,
  title         text,
  content_hash  text NOT NULL,                  -- reindexar só o que mudou
  version       int NOT NULL DEFAULT 1,
  updated_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, source_uri),
  UNIQUE (tenant_id, id)
);

CREATE TABLE kb_chunks (
  id               uuid PRIMARY KEY DEFAULT uuidv7(),
  tenant_id        uuid NOT NULL,
  document_id      uuid NOT NULL,
  ordinal          int NOT NULL,
  content          text NOT NULL,
  context          text,                        -- Contextual Retrieval: contexto do chunk no documento
  embedding        halfvec(1024) NOT NULL,      -- dimensão do modelo do ADR; trocar de modelo = nova coluna + reindexação
  embedding_model  text NOT NULL,
  tsv              tsvector GENERATED ALWAYS AS
                   (to_tsvector('portuguese', coalesce(context, '') || ' ' || content)) STORED,
  UNIQUE (document_id, ordinal),
  FOREIGN KEY (tenant_id, document_id) REFERENCES kb_documents (tenant_id, id) ON DELETE CASCADE
);
CREATE INDEX kb_chunks_embedding_idx ON kb_chunks USING hnsw (embedding halfvec_cosine_ops);
CREATE INDEX kb_chunks_tsv_idx ON kb_chunks USING gin (tsv);
CREATE INDEX kb_chunks_tenant_idx ON kb_chunks (tenant_id);

-- Atendimento humano, templates, outbox ----------------------------------
CREATE TABLE handoffs (
  id               uuid PRIMARY KEY DEFAULT uuidv7(),
  tenant_id        uuid NOT NULL,
  conversation_id  uuid NOT NULL,
  reason           text NOT NULL CHECK (reason IN ('user_request','repeated_failure','high_risk','out_of_scope','policy')),
  requested_at     timestamptz NOT NULL DEFAULT now(),
  assigned_to      text,
  resolved_at      timestamptz,
  FOREIGN KEY (tenant_id, conversation_id) REFERENCES conversations (tenant_id, id)
);
CREATE INDEX handoffs_conversation_idx ON handoffs (conversation_id);
CREATE INDEX handoffs_open_idx ON handoffs (tenant_id, requested_at) WHERE resolved_at IS NULL;

CREATE TABLE message_templates (
  id                  uuid PRIMARY KEY DEFAULT uuidv7(),
  tenant_id           uuid NOT NULL,
  channel_account_id  uuid NOT NULL,
  name                text NOT NULL,
  language            text NOT NULL,
  category            text NOT NULL CHECK (category IN ('marketing','utility','authentication')),
  status              text NOT NULL,           -- espelho do provider: APPROVED, REJECTED, PAUSED...
  components          jsonb NOT NULL,
  synced_at           timestamptz NOT NULL DEFAULT now(),
  UNIQUE (channel_account_id, name, language),
  FOREIGN KEY (tenant_id, channel_account_id) REFERENCES channel_accounts (tenant_id, id)
);

CREATE TABLE outbox (
  id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  tenant_id        uuid NOT NULL REFERENCES tenants(id),
  topic            text NOT NULL,              -- ex.: message.send, handoff.notify
  payload          jsonb NOT NULL,
  idempotency_key  text NOT NULL UNIQUE,
  available_at     timestamptz NOT NULL DEFAULT now(),
  attempts         int NOT NULL DEFAULT 0,
  processed_at     timestamptz,
  last_error       text
);
CREATE INDEX outbox_pending_idx ON outbox (available_at) WHERE processed_at IS NULL;
CREATE INDEX outbox_tenant_idx ON outbox (tenant_id);
-- Consumo: SELECT ... WHERE processed_at IS NULL AND available_at <= now()
--          ORDER BY available_at LIMIT 50 FOR UPDATE SKIP LOCKED;
```

Regra de índice para FK composta: basta um índice que comece pela coluna seletiva da FK (ex.: `conversation_id`), porque a checagem filtra por `tenant_id` e por ela.

## Escritas que pedem cuidado

Status só para frente, com janela de tempo para podar partições:

```sql
UPDATE messages SET status = $3
WHERE provider = $1 AND provider_message_id = $2
  AND created_at > now() - interval '7 days'
  AND (
    ($3 = 'failed' AND status IN ('queued','sent'))
    OR array_position(ARRAY['received','queued','sent','delivered','read','played'], status)
       < array_position(ARRAY['received','queued','sent','delivered','read','played'], $3)
  );
-- 0 linhas: repetir com janela de 30 dias e registrar no log antes de descartar.
```

Identidade de contato com BSUID: ao receber um BSUID novo num número, procurar o mesmo BSUID em `contact_channels` do mesmo tenant cujas contas tenham o mesmo `business_portfolio_id`; se achar, criar o novo `contact_channels` apontando para o mesmo `contact_id`. Quando telefone e BSUID chegarem juntos, gravar os dois na mesma linha.

## Partições

- Um job cria as partições com 3 meses de antecedência e alerta se restarem menos de 2 partições futuras. Sem partição `DEFAULT`, uma inserção fora das faixas falha com erro; o evento continua na inbox e é reprocessado depois que a partição existir.
- Criar a partição separada e anexar, que trava o pai só em `SHARE UPDATE EXCLUSIVE`; `CREATE TABLE ... PARTITION OF` trava o pai em `ACCESS EXCLUSIVE` ([PG: particionamento](https://www.postgresql.org/docs/current/ddl-partitioning.html)):

```sql
SET lock_timeout = '5s';
SET statement_timeout = '60s';
CREATE TABLE messages_2026_10 (LIKE messages INCLUDING DEFAULTS INCLUDING CONSTRAINTS);
ALTER TABLE messages_2026_10 ADD CONSTRAINT messages_2026_10_bounds
  CHECK (created_at >= '2026-10-01' AND created_at < '2026-11-01');
ALTER TABLE messages ATTACH PARTITION messages_2026_10
  FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');
ALTER TABLE messages_2026_10 DROP CONSTRAINT messages_2026_10_bounds;
```

- Retenção: `ALTER TABLE ... DETACH PARTITION ... CONCURRENTLY` e depois `DROP TABLE`, muito mais barato que `DELETE`. Só funciona sem partição default.
- Quando particionar: a documentação do Postgres indica ganho quando a tabela passa do tamanho da memória do servidor; o planner lida bem com até alguns milhares de partições se a poda funcionar (mesma fonte). Se a projeção de 24 meses de `messages` não chegar perto disso, uma tabela comum com índice BRIN em `created_at` e retenção por exclusão em lotes pode bastar. Converter depois é caro: decidir agora com a projeção.
- pg_partman 5.x automatiza criação e retenção e requer PG 14+ ([pg_partman](https://github.com/pgpartman/pg_partman)). Conferir se o Postgres gerenciado do PaaS oferece a extensão e como ela cria partições; se não houver, usar o job acima.

## Multi-tenant com RLS

```sql
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations FORCE ROW LEVEL SECURITY;  -- aplica também ao dono da tabela
CREATE POLICY tenant_isolation ON conversations
  USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
-- Na aplicação, dentro da transação:
--   SELECT set_config('app.tenant_id', $1, true);
```

- O `NULLIF` é necessário: depois do primeiro `set_config(..., true)` numa conexão, `current_setting` devolve `''` (e não nulo) nas transações seguintes, e `''::uuid` dá erro. Com `NULLIF`, sem tenant definido a política não retorna linhas (falha fechada).
- Superusuários e papéis com `BYPASSRLS` ignoram RLS: a aplicação conecta com um papel sem esses atributos e que não é dono das tabelas ([PG: RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)).
- `set_config(..., true)` vale só para a transação, compatível com PgBouncer em modo transação; `SET` de sessão não é ([PgBouncer](https://www.pgbouncer.org/features.html)).
- Tabelas de sistema sem RLS: `channel_accounts` (configuração, consultada pelo webhook antes de saber o tenant), `inbound_events`, `message_status_events`, `outbox`. Protegê-las por `GRANT` por papel: ingestão (insere na inbox e lê contas), worker (processa e define o tenant de cada job depois de resolver a conta), aplicação (sem acesso à inbox).
- Indexar as colunas usadas nas políticas ([Supabase: RLS](https://supabase.com/docs/guides/database/postgres/row-level-security)).
- Single-tenant: manter `tenant_id` mesmo assim custa pouco e evita migração se o produto virar SaaS. Decidir no documento.

## LGPD: eliminação e retenção

Eliminação de um titular é um job explícito, numa transação, com o tenant definido, nesta ordem:
1. `tool_calls` dos `llm_runs` das conversas do contato; depois `llm_runs` dessas conversas
2. `messages` dessas conversas (todas as partições) e a mídia correspondente no storage
3. `handoffs` e `conversations`
4. `contact_facts` e `contact_channels`
5. `contact_consents`: manter só o mínimo exigido por obrigação legal (art. 16, I), se houver; senão eliminar
6. `contacts`
7. `inbound_events` dos últimos 14 dias que contenham o telefone ou BSUID do contato (varredura limitada pela retenção curta)
8. traces no Langfuse e eventos no Sentry ligados ao hash do contato

- Para estatísticas, guardar agregados sem identificação em vez de manter linhas anonimizadas.
- Hash de telefone é pseudonimização, não anonimização (art. 13, §4º).
- Fonte: [Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm), arts. 12, 13, 15, 16 e 18.

## pgvector

- HNSW: melhor relação velocidade e recall que IVFFlat e pode ser criado com a tabela vazia. Padrões: `m = 16`, `ef_construction = 64`, `hnsw.ef_search = 40`.
- Filtro por tenant: o filtro é aplicado depois da varredura do índice; com `ef_search = 40` e um filtro que mantém 10% das linhas, voltam cerca de 4 resultados. Usar varreduras iterativas (0.8.0+): `SET LOCAL hnsw.iterative_scan = relaxed_order` (ou `strict_order`) e ajustar `hnsw.max_scan_tuples`. Com poucos tenants grandes, considerar índices parciais ou partições por tenant.
- Quando cada tenant tem poucos chunks, o planner prefere o índice de `tenant_id` e faz busca exata (recall de 100%), ignorando o HNSW; foi o que aconteceu no teste com 2.000 chunks por tenant. O ajuste acima importa quando a base de um tenant cresce. Conferir com `EXPLAIN` no volume real.
- Dimensão: `vector` indexa até 2.000 dimensões e `halfvec` até 4.000. A coluna tem dimensão fixa: trocar de modelo de embedding exige coluna nova, reindexação e troca da consulta.
- Versão: 0.8.7 ou superior (corrige um buffer overflow na construção de índices IVFFlat).
- Fonte: [pgvector README e CHANGELOG](https://github.com/pgvector/pgvector).

## Pooling

- PgBouncer em modo transação quebra `SET` de sessão, `LISTEN`, `PREPARE` em SQL e advisory locks de sessão ([PgBouncer](https://www.pgbouncer.org/features.html)). Advisory lock de transação (`pg_advisory_xact_lock`) funciona.
- Migrações sempre por conexão direta, não pelo pooler (Supabase: porta 6543 é o pooler em modo transação; Neon: host `-pooler`).
- Prisma 7: URL direta em `prisma.config.ts` para migrações ([Prisma + PgBouncer](https://www.prisma.io/docs/orm/prisma-client/setup-and-configuration/databases-connections/pgbouncer)).

## Troca de provider de um número

Atualizar a linha existente de `channel_accounts` (provider, `provider_app_ref`, `external_account_id`, `credentials_ref`) em vez de criar outra: o `id` se mantém e o histórico de conversas continua ligado ao número.
