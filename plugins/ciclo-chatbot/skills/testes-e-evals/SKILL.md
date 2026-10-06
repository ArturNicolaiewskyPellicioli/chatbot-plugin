---
name: testes-e-evals
description: Monta e roda a estratégia de qualidade do chatbot de WhatsApp com IA, cobrindo testes unitários, de integração com Postgres real, de contrato por provider, ponta a ponta, evals de conversa e red team com promptfoo e teste de carga com k6, com metas definidas na descoberta e verificação com evidência. Usar quando o usuário disser "testar o bot", "rodar evals", "red team", "teste de carga", "o bot está bom?", "regressão de prompt", ou na fase 7 do /ciclo-chatbot:iniciar.
argument-hint: "[tudo | unit | integracao | contrato | evals | redteam | carga]"
---

# Testes e evals

Estratégia detalhada em `${CLAUDE_SKILL_DIR}/references/estrategia-testes.md`. Saída: `docs/chatbot/07-qualidade.md` com resultados, metas e lacunas.

## Passos

1. Ler as metas da descoberta (taxa de aprovação nas evals, latência, pico de mensagens). Sem meta, propor uma e pedir aprovação antes de medir.
2. Rodar as camadas pedidas em `$ARGUMENTS` (padrão `tudo`), na ordem da referência: unitários → integração → contrato → ponta a ponta → evals → red team → carga.
3. Evals: com a skill `promptfoo-evals` do plugin `promptfoo`, expandir o conjunto da fase 4 com as falhas encontradas na implementação. Rodar cada caso crítico k vezes (pass^k).
4. Red team: com `promptfoo-redteam-setup` e `promptfoo-redteam-run`, cobrir injeção de prompt, vazamento de dados de outros contatos e do system prompt, jailbreak, fora de escopo, consumo abusivo. Escopo e plugins do red team ligados ao OWASP mapeado na fase 4.
5. Carga: k6 contra staging (nunca contra a Meta): rajada de webhooks com lotes grandes e duplicatas, medindo tempo até o 200 e atraso da fila.
6. Para falhas, usar `superpowers:systematic-debugging` antes de propor correção.
7. Antes de declarar a fase pronta, `superpowers:verification-before-completion`: anexar a saída dos comandos ao documento.
8. Rodar o checklist da fase 7 e apresentar o portão com números, não adjetivos.
