# Migrações seguras

Objetivo: nenhuma migração derruba o bot. Durante um deploy sem downtime, a versão antiga e a nova do código rodam ao mesmo tempo contra o mesmo banco.

## Regras

1. **Expandir e contrair.** Adicionar (coluna, tabela, índice) numa migração; trocar o código para usar a novidade; remover o antigo numa migração posterior, depois que nenhuma versão em produção depende dele.
2. **`lock_timeout` em toda migração**, por sessão (`SET lock_timeout = '5s';`), nunca no `postgresql.conf` ([PG: configuração do cliente](https://www.postgresql.org/docs/current/runtime-config-client.html)). Se estourar, a migração falha em vez de travar o tráfego; repetir em horário calmo.
3. **Índices com `CREATE INDEX CONCURRENTLY`.** Não roda dentro de transação. Se falhar, deixa um índice `INVALID`: apagar e recriar ([PG: CREATE INDEX](https://www.postgresql.org/docs/current/sql-createindex.html)). Em tabela particionada, `CONCURRENTLY` é recusado e o Squawk não avisa: criar `CREATE INDEX ... ON ONLY <pai>` (fica inválido), depois `CREATE INDEX CONCURRENTLY` em cada partição e `ALTER INDEX <índice do pai> ATTACH PARTITION <índice da partição>` para cada uma; o índice do pai fica válido quando todas estiverem anexadas ([PG: particionamento](https://www.postgresql.org/docs/current/ddl-partitioning.html)).
4. **Constraints em dois passos:** `ADD CONSTRAINT ... NOT VALID` e depois `VALIDATE CONSTRAINT`, que pega só um lock `SHARE UPDATE EXCLUSIVE` ([PG: ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)).
5. **`NOT NULL` em coluna existente:** primeiro um `CHECK (col IS NOT NULL) NOT VALID`, validar, e só então `SET NOT NULL` (o Postgres aproveita o check validado e pula a varredura).
6. **`DEFAULT` não volátil** não reescreve a tabela; volátil (ex.: `random()`) reescreve.
7. **Nunca** renomear ou mudar tipo de coluna em uso numa única migração: criar a nova, copiar em lotes, trocar o código, remover a antiga.
8. **Partições:** criar com `CREATE TABLE (LIKE ...)` + `CHECK` das faixas + `ATTACH PARTITION` (trava o pai só em `SHARE UPDATE EXCLUSIVE`); retirar com `DETACH PARTITION ... CONCURRENTLY`, que exige não haver partição `DEFAULT`. Exemplo em `modelo-referencia.md`.
9. **Migração roda no comando de pré-deploy do PaaS**, por conexão direta, nunca no boot da aplicação ([12factor XII](https://12factor.net/admin-processes)).

## Squawk

- Instalar: `npm i -g squawk-cli` ou `pip install squawk-cli`. CI: action `sbdchd/squawk-action`.
- O hook deste plugin roda `squawk` em todo arquivo `.sql` de migração gravado pelo Claude (pastas `migrations`, `migrate`, `drizzle`, `alembic`) e devolve os alertas para correção.
- Criar `.squawk.toml` na raiz do projeto; o Squawk o encontra sozinho:

  ```toml
  pg_version = "18.0"            # versão do Postgres do PaaS
  assume_in_transaction = true   # só se o runner do ORM envolve cada arquivo em transação
  ```

  Sem `assume_in_transaction`, o Squawk acusa índices criados sem `CONCURRENTLY` até em tabelas criadas no mesmo arquivo. Com ele, passa a acusar `CONCURRENTLY` dentro de transação, que é o erro real nesse caso. Conferir o comportamento do ORM antes de escolher.
- Exceção pontual: comentário `-- squawk-ignore-file <regra>` no topo do arquivo, com a justificativa na linha de cima.
- Migrações que não são `.sql` (Alembic em Python, TypeORM em TypeScript) não passam pelo hook. Gerar o SQL e rodar o Squawk nele, na fase 3 e no CI: Alembic em modo offline (`alembic upgrade <de>:<para> --sql > alembic/sql/<revisão>.sql`); TypeORM e outros, capturando o SQL emitido ao aplicar no banco local (log de queries) num arquivo `.sql` dentro de `migrations/`.
- Regras mais relevantes aqui: `require-concurrent-index-creation`, `ban-concurrent-index-creation-in-transaction`, `constraint-missing-not-valid`, `adding-field-with-default`, `changing-column-type`, `renaming-column`, `ban-drop-column`, `require-timeout-settings`, `prefer-timestamptz`, `prefer-identity`, `prefer-bigint-over-int` ([lista completa](https://squawkhq.com/docs/rules)).

## Por ORM

Conferir na documentação atual (Context7) antes de aplicar; o comportamento de transação muda entre versões.

| ORM | Pontos de atenção |
|---|---|
| Prisma | Migrações SQL geradas ficam em `prisma/migrations/*/migration.sql` e podem ser editadas antes de aplicar. Particionamento, `halfvec`, índices HNSW e RLS exigem SQL manual na migração. Verificar se o runner envolve o arquivo em transação antes de usar `CONCURRENTLY`; se envolver, isolar o índice numa migração própria conforme a documentação. Negar `migrate reset` em ambientes compartilhados |
| Drizzle | `drizzle-kit generate` produz SQL revisável; mesmos cuidados com SQL manual e transação |
| TypeORM | Migrações em TypeScript; `transaction = false` na classe da migração para `CONCURRENTLY` (conferir na versão usada) |
| Alembic | `op.get_context().autocommit_block()` para `CONCURRENTLY` ([Alembic runtime](https://alembic.sqlalchemy.org/en/latest/api/runtime.html)); autogenerate não detecta tudo, revisar o arquivo |

## Alternativa

`pgroll` (xataio/pgroll, Apache-2.0) faz expandir e contrair automaticamente com views versionadas, mas não combina com migrações geradas por ORM. Considerar só se o projeto não usar ORM para migrações.
