---
name: providers-whatsapp
description: Desenha e implementa a camada modular de providers de WhatsApp (ports and adapters) com a WhatsApp Cloud API oficial da Meta como padrão e a possibilidade de trocar de provider ou usar dois ao mesmo tempo (360dialog, Gupshup, Twilio, Evolution API), incluindo eventos normalizados, pipeline de webhook com assinatura e idempotência, janela de 24h, limites de vazão, BSUID, mídia, templates e roteamento por número. Usar quando o usuário disser "integrar WhatsApp", "adapter de provider", "trocar de provider", "usar dois providers", "webhook do WhatsApp", "Evolution API", "Twilio WhatsApp", ou na fase 5 do /ciclo-chatbot:iniciar.
argument-hint: "[desenho | adapter <provider> | revisar]"
---

# Providers de WhatsApp

Regra central: o núcleo do bot fala só com a porta `MessagingProvider` e com eventos normalizados. Nenhum módulo fora de `adapters/` conhece payload, header ou código de erro de provider.

Material de apoio em `${CLAUDE_SKILL_DIR}/references/`:
- `cloud-api.md`: fatos da WhatsApp Cloud API com fontes (versões, webhooks, assinatura, janela, limites, mídia, BSUID, preços, políticas)
- `porta-adapters.md`: interface, eventos normalizados, erros, pipeline de webhook, serviços do núcleo, roteamento e dois providers simultâneos
- `providers.md`: providers alternativos, diferenças de payload e assinatura, risco de banimento

## Modo `desenho` (fase 5)

1. Ler a descoberta (números, provider secundário, templates, mídia, multi-tenant) e o modelo de dados aprovado.
2. Conferir fatos voláteis antes de escrever: versão atual da Graph API e mudanças recentes no [changelog da Cloud API](https://developers.facebook.com/documentation/business-messaging/whatsapp/changelog). Atualizar `cloud-api.md` mentalmente com o que mudou e registrar a data no documento.
3. Disparar o agente `especialista-whatsapp` com os caminhos acima e pedir `docs/chatbot/05-whatsapp.md` contendo:
   - interface da porta na linguagem do ADR 0001
   - lista de adapters com a flag `official` e as capacidades de cada um
   - pipeline do webhook passo a passo (rota, corpo bruto, assinatura, inbox, fila, 200)
   - serviços do núcleo: janela de 24h, limitador de vazão, envio com retentativa por tipo de erro, mídia, templates, custo
   - roteamento por número e política para dois providers simultâneos
   - plano de testes de contrato por adapter com payloads gravados
4. Se houver adapter Twilio, usar as skills do plugin `twilio-developer-kit`. Se houver 360dialog, o MCP oficial da 360dialog ajuda a configurar canal, webhooks e templates.
5. Rodar o checklist da fase 5 e apresentar o portão.

## Modo `adapter <provider>` (durante a fase 6)

Implementar um adapter seguindo `porta-adapters.md`, com TDD (`superpowers:test-driven-development`):
1. Testes de contrato primeiro, com payloads reais anonimizados do provider: mensagem de texto, mídia, resposta interativa, status em ordem e fora de ordem, lote com várias atualizações, duplicata, mensagem sem telefone (só BSUID), assinatura inválida.
2. `verifySignature` sobre o corpo bruto, com comparação em tempo constante.
3. `parseWebhook` produz só eventos normalizados; campos desconhecidos vão para `raw`.
4. `send` traduz erros do provider para `NormalizedError`.
5. Declarar `capabilities` com valores conferidos na documentação do provider.

## Modo `revisar`

Conferir uma implementação existente contra `porta-adapters.md` e o checklist da fase 5. Prioridade: assinatura, idempotência, BSUID, janela de 24h, vazamento de tipos de provider para fora dos adapters.
