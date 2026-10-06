---
name: camada-ia
description: Desenha a camada de IA de um chatbot de WhatsApp com as melhores peças da comunidade (skill claude-api da Anthropic, llm-application-dev do wshobson, promptfoo), cobrindo pipeline por mensagem (guarda, roteador, handlers), modelos por papel, cache de prompt, RAG com recuperação híbrida e rerank, memória de conversas longas, ferramentas com privilégio mínimo, guardrails OWASP, transbordo humano, prompts versionados e conjunto inicial de evals. Usar quando o usuário disser "desenhar a IA do bot", "prompt do chatbot", "RAG", "base de conhecimento", "memória do bot", "guardrails", "evals", ou na fase 4 do /ciclo-chatbot:iniciar.
argument-hint: "[novo | revisar]"
---

# Camada de IA

Entradas: descoberta (intenções, base de conhecimento, integrações, transbordo, LGPD), ADR 0004 (provider, modelos, framework) e o modelo de dados aprovado. Saídas: `docs/chatbot/04-ia.md`, prompts versionados em `prompts/`, conjunto inicial de evals em `evals/`.

Material de apoio em `${CLAUDE_SKILL_DIR}/references/`:
- `arquitetura-ia.md`: pipeline, modelos por papel, cache, memória, ferramentas, UX no WhatsApp
- `rag.md`: quando usar RAG, Contextual Retrieval, busca híbrida, rerank, citações
- `guardrails-evals.md`: OWASP LLM Top 10 (2025) e Agentic Top 10, LGPD, transbordo, método de evals

## 1. Conhecimento atualizado

Modelos, preços e recursos de API mudam a cada poucos meses. Antes de decidir:
- Provider Anthropic: invocar a skill `claude-api` (marketplace `anthropic-agent-skills`) para modelos atuais, preços, prompt caching, structured outputs e tool use.
- Outros providers ou frameworks: consultar a documentação pelo MCP Context7.
- RAG e evals: invocar, se instaladas, as skills do plugin `llm-application-dev` (`rag-implementation`, `hybrid-search-implementation`, `embedding-strategies`, `vector-index-tuning`, `prompt-engineering-patterns`, `llm-evaluation`). Algumas referências de modelos nessas skills estão desatualizadas: valem os padrões, não os nomes de modelo.

## 2. Desenhar

Disparar o agente `engenheiro-ia` deste plugin com os caminhos das entradas, do material de apoio e das skills disponíveis. Pedir `docs/chatbot/04-ia.md` com:
1. Diagrama do pipeline por mensagem e orçamento de latência por etapa.
2. Tabela de modelos por papel (guarda, roteador, resposta, resumo, juiz de eval) com preço por milhão de tokens conferido na data e custo estimado por conversa.
3. Estratégia de cache de prompt (o que fica no prefixo estável).
4. Decisão de RAG (base inteira no prompt com cache ou recuperação híbrida com rerank) com o tamanho da base em tokens.
5. Memória: janela de mensagens, resumo rolante, fatos do contato, o que não guardar.
6. Catálogo de ferramentas: nome, entrada, efeito colateral, permissão, exige aprovação humana?, chave de idempotência.
7. Matriz de guardrails ligada ao OWASP e gatilhos de transbordo.
8. Prompts em `prompts/<nome>@v<N>.md`; a versão é gravada em `llm_runs.prompt_version`.

## 3. Evals desde já

Com a skill `promptfoo-evals` (plugin `promptfoo`) ou manualmente:
- 20 a 50 casos tirados das mensagens reais da descoberta, cobrindo cada intenção, fora de escopo, transbordo, injeção de prompt, pedido de dado pessoal de terceiros e mensagens longas ou com áudio transcrito.
- Critério por caso: verificação por código quando possível; rubrica de LLM com saída discreta quando não.
- Configuração em `evals/promptfooconfig.yaml`, pronta para rodar no CI (fase 7).

## 4. Portão

Rodar o checklist da fase 4 e apresentar: pipeline, custo estimado por conversa (LLM + Meta), decisões de RAG e memória, ferramentas que exigem aprovação humana e o conjunto de evals.
