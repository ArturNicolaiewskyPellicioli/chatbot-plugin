# Estrutura modular

Monólito modular com dois processos (`web` e `worker`) no mesmo repositório e no mesmo build.

## Pastas (TypeScript; em Python, mesma ideia com pacotes)

```
src/
  apps/
    web/                 # HTTP: rotas de webhook, health checks, API interna
    worker/              # consumidores da fila, jobs agendados
  modules/
    conversations/       # conversas, mensagens, janela de 24h, transbordo
    contacts/            # contatos, identidades, consentimentos, fatos
    ai/                  # pipeline: guarda, roteador, handlers, prompts, memória
    knowledge/           # ingestão e busca na base de conhecimento
    messaging/           # porta MessagingProvider, serviços do núcleo (envio, vazão, status, mídia, templates)
      adapters/
        meta-cloud/      # Meta, 360dialog, Gupshup
        twilio/
        evolution/
    billing/             # custos de LLM e de mensagens
  shared/
    db/                  # conexão, transação com tenant, repositórios base
    queue/               # abstração da fila
    config/              # leitura e validação de variáveis
    observability/       # logger, tracing, métricas
    errors/
prompts/                 # prompts versionados
evals/                   # promptfoo
migrations/              # ou a pasta do ORM
test/fixtures/providers/ # payloads de webhook por provider
```

## Regras de dependência

| De | Pode importar | Não pode importar |
|---|---|---|
| `apps/*` | `modules/*` (API pública de cada módulo), `shared/*` | internos de módulos |
| `modules/X` | `shared/*`, API pública de outros módulos | internos de outros módulos, `apps/*` |
| `modules/messaging/adapters/*` | porta e tipos de `messaging`, `shared/*` | qualquer outro módulo |
| `shared/*` | bibliotecas externas | `modules/*`, `apps/*` |

Cada módulo expõe sua API num único arquivo de entrada (`index.ts` / `__init__.py`). Verificar no CI com `dependency-cruiser` ou `eslint-plugin-boundaries` (TypeScript) ou `import-linter` (Python).

## Duplicação

- `jscpd` no CI com limite baixo (ex.: 1% e mínimo de 50 tokens por bloco) e relatório anexado ao PR.
- Duplicação de conceito também conta: duas funções que formatam telefone de jeitos diferentes são um bug esperando para acontecer, mesmo com textos diferentes.

## Ambiente local

```yaml
# compose.yaml (desenvolvimento)
services:
  postgres:
    image: pgvector/pgvector:pg18
    environment:
      POSTGRES_PASSWORD: dev
    ports: ["54329:5432"]
    volumes: ["pgdata:/var/lib/postgresql"]
  redis:
    image: redis:7
    command: ["redis-server", "--appendonly", "yes", "--maxmemory-policy", "noeviction"]
    ports: ["6379:6379"]
volumes:
  pgdata: {}
```

Conferir as tags de imagem na data. A partir do Postgres 18 a imagem oficial guarda os dados em um subdiretório de `/var/lib/postgresql` por versão; conferir a documentação da imagem antes de mapear volumes. Webhook local: `cloudflared tunnel --url http://localhost:<porta>` (ou ngrok) e cadastrar a URL HTTPS no app Meta de desenvolvimento. Redis com `noeviction` e AOF segue a recomendação do BullMQ para produção ([BullMQ](https://docs.bullmq.io/guide/going-to-production)).

## Fatias sugeridas

| Fatia | Conteúdo | Pronto quando |
|---|---|---|
| 0 Esqueleto | webhook com assinatura, inbox, fila, worker, resposta fixa, status | mensagem real do número de teste recebe resposta e status gravados |
| 1 Identidade e conversa | contatos com telefone ou BSUID, conversas, janela de 24h, linha do tempo | testes de contrato com payload sem telefone passam |
| 2 IA básica | guarda, roteador, resposta com prompt versionado, `llm_runs` | evals de regressão iniciais passam |
| 3 Base de conhecimento | ingestão, busca (ou base inteira em cache), citações | recall@K medido e acima da meta |
| 4 Ferramentas de negócio | integrações da descoberta, aprovação humana, idempotência | ações com consequência exigem confirmação |
| 5 Transbordo e templates | handoff, retorno fora da janela com template, sincronização de templates | fluxo completo testado |
| 6 Mídia | download e cópia, áudio → transcrição | áudio real respondido |
| 7 Operação | custos, retenção, anonimização (LGPD), limites por contato | jobs testados |

Ajustar à descoberta; a ordem 0 → 1 → 2 vale sempre.
