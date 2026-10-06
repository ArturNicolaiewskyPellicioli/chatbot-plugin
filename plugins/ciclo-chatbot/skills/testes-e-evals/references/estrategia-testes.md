# Estratégia de testes

| Camada | O que cobre | Ferramenta | Roda no CI? |
|---|---|---|---|
| Unitários | regras do domínio (janela de 24h, transição de status, limitador de vazão, roteamento por capacidade), parsers dos adapters | test runner da stack | sim |
| Integração | repositórios, migrações do zero, RLS, consultas críticas, outbox com `SKIP LOCKED` | Testcontainers ou serviço `pgvector/pgvector` no CI | sim |
| Contrato por provider | `verifySignature`, `parseWebhook`, tradução de erros, com payloads gravados | fixtures em `test/fixtures/providers/<provider>/` | sim |
| Ponta a ponta | webhook simulado → worker → adapter falso que grava o envio | app real + fila real + provider falso | sim |
| Evals de conversa | respostas por intenção, transbordo, fora de escopo | promptfoo | sim, com meta |
| Red team | injeção, vazamento, jailbreak, consumo | promptfoo redteam | antes de cada release |
| Carga | tempo até 200, atraso da fila, conexões no banco | k6 | antes do go-live e de mudanças grandes |

## Casos obrigatórios de contrato (todos os adapters)

- mensagem de texto; mídia; resposta de botão e de lista
- lote com mensagens e status misturados
- duplicata exata (mesmo ID) → um evento só no banco
- status fora de ordem (`read` antes de `delivered`) → status final `read`
- mensagem sem telefone, só BSUID
- assinatura inválida, ausente, e corpo alterado depois de assinado
- payload com campo desconhecido → não quebra; vai para `raw`

## Evals

- Formato: `evals/promptfooconfig.yaml` com provedores apontando para o pipeline real (função ou endpoint de teste), não para o modelo cru.
- Asserções determinísticas primeiro (contém link certo, não contém telefone, tamanho ≤ 4.096, chamou a ferramenta X), rubrica de LLM depois.
- Multi-turno com usuário simulado para fluxos de transação e transbordo.
- No CI, a action `promptfoo/promptfoo-action` falha o PR abaixo da meta ([CI](https://www.promptfoo.dev/docs/integrations/ci-cd/)).
- Fontes de método: [Anthropic: develop tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests), [Anthropic: evals for agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).

## Carga

- Perfil mínimo: pico por minuto da descoberta × 3, com lotes de 50 a 1.000 atualizações por webhook (o máximo que a Meta envia por lote) e 5% de duplicatas.
- Metas: p99 do tempo até o 200 bem abaixo de um segundo; fila sem crescimento contínuo; nenhum erro de conexão com o banco.
- Rodar contra staging com o adapter de envio apontando para um provider falso, para não gastar mensagens nem violar limites da Meta.
