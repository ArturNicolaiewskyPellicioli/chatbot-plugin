---
name: modelar-banco
description: Desenha, valida e revisa o banco PostgreSQL de um chatbot com IA para WhatsApp, orquestrando as melhores skills da comunidade (Supabase Postgres best practices, pg-aiguide da TigerData, database-design do wshobson), um arquiteto e um revisor adversarial, Squawk para migrações e Postgres MCP Pro para saúde e índices, com teste em volume projetado. Cobre modelo multi-provider, idempotência de webhook, particionamento, pgvector, índices, multi-tenant com RLS, pooling, migrações seguras e LGPD. Usar quando o usuário disser "modelar o banco", "desenhar o schema", "banco escalável", "revisar meu banco", "índices", "particionar mensagens", "pgvector", ou na fase 3 do /ciclo-chatbot:iniciar.
argument-hint: "[novo | revisar <caminho do schema>]"
---

# Banco de dados

O banco é o coração do chatbot. Esta fase só termina quando o modelo foi desenhado com conhecimento da comunidade, revisado por agentes independentes e validado num Postgres real com volume projetado.

Entradas: `docs/chatbot/01-descoberta.md` (volumes, retenção, multi-tenant, base de conhecimento) e os ADRs de ORM e stack. Em modo `revisar`, o schema existente é a entrada principal e o passo 3 vira uma revisão.

Material de apoio deste plugin, em `${CLAUDE_SKILL_DIR}/references/`:
- `modelo-referencia.md`: modelo de dados de referência para chatbot multi-provider, com DDL comentado
- `checklist-banco.md`: checklist de revisão com fontes
- `migracoes-seguras.md`: regras de migração sem downtime, por ORM
- `validacao-volume.md`: roteiro de teste com dados sintéticos e `EXPLAIN`

## 1. Reunir conhecimento da comunidade

Invocar, na ordem, as skills instaladas (ver nomes exatos na lista da sessão) e anotar as regras que se aplicam ao projeto:

| Skill | Para quê (uma fonte principal por assunto) |
|---|---|
| `postgres-best-practices:supabase-postgres-best-practices` | regras de índices, tipos, chaves, FKs, RLS, pooling, locks, paginação, upsert |
| `pg:design-postgres-tables` | desenho de tabelas e tipos |
| `pg:pgvector-semantic-search` e `pg:postgres-hybrid-text-search` | busca vetorial e híbrida, se houver RAG |
| `pg:postgres-database-migration` | migrações (complementa `migracoes-seguras.md`) |
| skills do ORM (ex.: `prisma-*`) | limitações do ORM: o que precisa de SQL bruto |

Quando duas fontes divergirem, registrar as duas posições e a escolha no documento da fase, com o motivo.

Se nenhuma estiver instalada, oferecer `ciclo-chatbot:preparar-ambiente banco`. Se o usuário recusar, seguir com o material de apoio deste plugin e registrar no estado.

## 2. Desenhar

Disparar o agente `arquiteto-dados` deste plugin com:
- caminhos da descoberta, dos ADRs e dos arquivos de referência acima (caminho absoluto de `${CLAUDE_SKILL_DIR}/references/`)
- a lista de regras coletadas no passo 1
- o pedido de saída: `docs/chatbot/03-banco.md` (ERD em Mermaid, dicionário de dados, tabela "consulta crítica → índice", decisões de chave, particionamento, pgvector, multi-tenant, pooling, retenção e LGPD, projeção de tamanho em 12 e 24 meses), schema no ORM e migrações SQL

## 3. Revisar em paralelo, de forma independente

Disparar, na mesma mensagem, dois revisores que não veem a opinião um do outro:
1. Agente `revisor-banco` deste plugin, com o `checklist-banco.md` e o `migracoes-seguras.md`.
2. Agente `database-architect` do plugin `database-design` (wshobson), se instalado, com o pedido: "revise este schema para escala, integridade e desempenho; liste problemas por severidade com a consulta afetada".

Entregar as duas revisões ao `arquiteto-dados` para consolidar. Divergência entre revisores vira pergunta ao usuário com as duas posições e as fontes. Repetir até não haver bloqueio aberto (máximo de três rodadas; depois disso, levar ao usuário).

## 4. Validar num Postgres real

Seguir `validacao-volume.md`:
1. Subir Postgres com pgvector localmente (Docker ou Testcontainers) na mesma versão maior do PaaS escolhido.
2. Criar o `.squawk.toml` do projeto (ver `migracoes-seguras.md`) e aplicar as migrações do zero. O hook deste plugin roda o Squawk em cada arquivo de migração `.sql` gravado; corrigir todo alerta ou justificar no documento.
3. Gerar dados sintéticos no volume projetado de 12 meses.
4. Rodar `EXPLAIN (ANALYZE, BUFFERS)` em cada consulta crítica e registrar o plano resumido no documento.
5. Se o Postgres MCP Pro estiver configurado para esse banco local, rodar `analyze_db_health` e `analyze_workload_indexes` e incorporar o que fizer sentido.

## 5. Portão

Rodar o checklist da fase 3 (em `ciclo-chatbot:iniciar`, `references/fases.md`) e apresentar:
- ERD resumido e as cinco decisões de maior impacto
- tabela de consultas críticas com o índice usado e o tempo medido
- achados dos revisores e como foram resolvidos
- o que fica para revisitar e com qual gatilho (ex.: "particionar `llm_runs` quando passar de X GB")
