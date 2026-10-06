# Arquitetura da camada de IA

## Workflow antes de agente

A Anthropic separa *workflows* (caminhos definidos em código) de *agentes* (o modelo decide os passos) e recomenda começar pela solução mais simples. Padrões úteis aqui: roteamento, encadeamento de prompts, paralelização e avaliador-otimizador. Ferramentas devem ser desenhadas para dificultar o erro ("poka-yoke") ([Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)).

Para um bot de atendimento, o guia de suporte da Anthropic sugere classificar a intenção antes de responder, manter o papel no system prompt e organizar o contexto estático em blocos ([Customer support chat](https://platform.claude.com/docs/en/about-claude/use-case-guides/customer-support-chat)).

## Pipeline por mensagem (referência)

```
webhook → inbox idempotente → fila
worker (uma conversa por vez, com debounce curto para juntar rajadas;
        ver "Uma conversa por vez" em providers-whatsapp/references/porta-adapters.md):
  1. carregar contexto (contato, janela de 24h, conversa, resumo, fatos)
  2. normalizar entrada (áudio → transcrição; mídia → descrição ou recusa)
  3. marcar como lida + indicador de digitação
  4. guarda de entrada (modelo pequeno, saída estruturada): injeção, abuso, dado sensível
  5. roteador (modelo pequeno, saída estruturada): intenção + confiança
  6. handler da intenção:
       - pergunta → resposta com base de conhecimento (RAG ou base inteira em cache)
       - transação → agente com ferramentas limitadas àquela intenção
       - transbordo → abre handoff, avisa o contato
  7. checagem de saída: tamanho, formato do canal, política, vazamento de dados
  8. enviar pelo adapter do provider (outbox) e gravar llm_runs/tool_calls
```

## Modelos por papel

| Papel | Perfil | Observação |
|---|---|---|
| Guarda e roteador | menor e mais rápido do provider | saída estruturada com schema estrito |
| Resposta | modelo intermediário | onde vai a maior parte do custo |
| Casos difíceis | modelo maior | só por regra explícita (confiança baixa, intenção crítica) |
| Juiz de evals | modelo maior | roda offline; batch quando possível |
| Resumo da conversa | modelo pequeno | assíncrono |

Nomes e preços: conferir na data pela skill `claude-api` ou na [visão geral de modelos](https://platform.claude.com/docs/en/about-claude/models/overview). A Anthropic indica o modelo menor quando a prioridade é latência ([reduzir latência](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-latency)). A API de batch tem 50% de desconto e serve para evals offline ([batch](https://platform.claude.com/docs/en/build-with-claude/batch-processing)).

## Cache de prompt (Anthropic)

- A ordem do prefixo é ferramentas → system → mensagens. Colocar no início o que não muda (ferramentas, instruções, base de conhecimento pequena) e marcar o ponto de cache depois disso.
- Nunca colocar data/hora, nome do contato ou outros dados por usuário antes do ponto de cache: invalida o cache para todos.
- Há tamanho mínimo de prefixo por modelo para o cache valer e limite de pontos de cache por requisição; conferir os números atuais na [documentação de prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching).
- Medir `cache_read_input_tokens` em `llm_runs` para provar que o cache está funcionando.

## Saída estruturada

Usar structured outputs (schema JSON) para guarda, roteador e qualquer decisão que o código consome; `strict: true` nas ferramentas ([structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)). Conferir na documentação as incompatibilidades atuais (por exemplo com citações).

## Memória em conversas longas

- Últimas N mensagens literais + resumo rolante (`conversations.summary`) + fatos duráveis do contato (`contact_facts`).
- Alternativas da API da Anthropic: compactação no servidor, edição de contexto e a ferramenta de memória ([janelas de contexto](https://platform.claude.com/docs/en/build-with-claude/context-windows), [memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)). Técnicas de contexto: compactação, notas estruturadas, recuperação sob demanda ([context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
- LGPD art. 6º (necessidade): guardar só fatos úteis ao atendimento; nada de inferências sobre saúde, religião etc. sem base legal ([Lei 13.709](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)).

## Ferramentas

- Uma lista de ferramentas por intenção, não todas para todos.
- Privilégio mínimo; parâmetros validados no código, nunca confiando no modelo.
- Ações com consequência (cancelar, cobrar, alterar cadastro) exigem confirmação explícita do contato ou de um humano.
- Efeito colateral externo sempre com chave de idempotência (`tool_calls.idempotency_key`).
- Resultado de ferramenta é dado não confiável: entra como `tool_result`, nunca concatenado ao system prompt.

## UX no WhatsApp

- Texto de até 4.096 caracteres por mensagem ([Meta: texto](https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/text-messages)).
- Preferir uma resposta consolidada a várias bolhas: desde 2026-10-01 a Meta anuncia cobrança também de mensagens de serviço ([preços](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing/non-template-messages)).
- Botões (até 3) e listas (até 10 linhas) quando o adapter tiver a capacidade; senão, menu numerado em texto ([botões](https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/interactive-reply-buttons-messages), [listas](https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/interactive-list-messages)).
- O indicador de digitação some após a resposta ou 25 segundos ([Meta](https://developers.facebook.com/documentation/business-messaging/whatsapp/typing-indicators)). Orçamento de latência: responder bem antes disso; se uma etapa lenta for passar do limite, mandar uma mensagem curta de espera.
- Áudio chega como OGG/Opus de até 16 MB ([Meta: áudio](https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/audio-messages)); conferir os formatos aceitos pela API de transcrição escolhida e manter conversão com ffmpeg como plano B.
