---
name: decidir-stack
description: Decide a arquitetura e a stack de um chatbot com IA para WhatsApp a cada projeto, com matriz de decisão ponderada, ADRs e diagramas C4, cobrindo linguagem e framework, ORM e migrações, fila, provider e framework de LLM, PaaS e região, estrutura modular e observabilidade. Usar quando o usuário disser "qual stack usar", "arquitetura do chatbot", "TypeScript ou Python", "escolher ORM", "escolher PaaS", "escrever ADR", ou na fase 2 do /ciclo-chatbot:iniciar.
argument-hint: "[restrições conhecidas, ex.: 'time só sabe TypeScript']"
---

# Arquitetura e stack

Entrada: `docs/chatbot/01-descoberta.md`. Saída: `docs/chatbot/02-arquitetura.md` e ADRs em `docs/adr/NNNN-titulo.md` (formato em `${CLAUDE_SKILL_DIR}/references/matriz-stack.md`).

## Ponto de partida (não negociável sem ADR)

- **Monólito modular com dois processos**: `web` (recebe webhooks e APIs internas) e `worker` (processa fila, chama LLM, envia mensagens). Microsserviços só com justificativa de escala ou de time registrada em ADR.
- **PostgreSQL** como banco principal, com pgvector se houver RAG. Versão 18 quando o PaaS oferecer (tem `uuidv7()` nativo); mínimo 16.
- **Redis ou Valkey** para fila e limites de vazão.
- **Webhook nunca processa de forma síncrona**: grava, enfileira, responde 200.
- **Começar pelo SDK do provider de LLM e por um fluxo explícito** (workflow), não por um framework de agentes. A Anthropic recomenda a solução mais simples que funcione e alerta que frameworks adicionam camadas que escondem prompts e respostas ([Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)). Framework só entra com ganho concreto registrado em ADR.

## Passos

1. Ler a descoberta e listar requisitos que pesam na stack: volume, multi-tenant, RAG, integrações, experiência do time, prazo, orçamento.
2. Preencher a matriz de `references/matriz-stack.md` com pesos combinados com o usuário. Conferir versões e estado de manutenção de cada opção com o MCP Context7 e registrar a data.
3. Pedir uma segunda opinião independente: se o plugin `feature-dev` estiver instalado, rodar o agente `code-architect` com a descoberta e a matriz e pedir duas alternativas de arquitetura com trade-offs. Comparar com a matriz e registrar divergências.
4. Escolher o PaaS e a região usando `${CLAUDE_PLUGIN_ROOT}/skills/publicar/references/paas.md`. Medir, não supor: o caminho crítico é Meta → seu servidor → API do LLM → Meta, e a região mais próxima do usuário final não é necessariamente a de menor latência nesse caminho.
5. Gerar diagramas C4 de contexto e de containers em Mermaid. Se o plugin `c4-architecture` estiver instalado, usar `/c4-architecture`.
6. Escrever os ADRs mínimos:
   - 0001 Linguagem e framework web
   - 0002 ORM e ferramenta de migração
   - 0003 Fila e worker
   - 0004 Provider de LLM, modelos por papel e framework (ou ausência dele)
   - 0005 PaaS, região e ambientes
   - 0006 Estrutura modular e regras de dependência entre módulos
   - 0007 Observabilidade (logs, traces, erros, traces de LLM)
   - 0008 Providers de WhatsApp: provider principal, secundário (se houver), roteamento por número e, se algum adapter tiver `official: false`, o risco de banimento aceito e onde ele pode rodar
7. Rodar `ciclo-chatbot:preparar-ambiente` com as camadas correspondentes à stack escolhida (`stack-ts` ou `stack-python`, deploy do PaaS escolhido).
8. Rodar o checklist da fase 2 e apresentar o portão.
