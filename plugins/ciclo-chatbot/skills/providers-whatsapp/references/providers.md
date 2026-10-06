# Providers alternativos

Conferido em 2026-10-06.

| Provider | Tipo | Formato e assinatura | Docs |
|---|---|---|---|
| Meta Cloud API | oficial, direto | formato Meta; `X-Hub-Signature-256` (HMAC-SHA256 com app secret) | [webhooks](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/overview) |
| 360dialog | BSP oficial | base `https://waba-v2.360dialog.io`, header `D360-API-KEY`; payloads e webhooks no formato Meta; webhooks assinados com `x-360dialog-signature`. O host antigo `waba.360dialog.io` (On-Premises) morreu em 2025-10-23 | [docs](https://docs.360dialog.com/docs/llms-full.txt) |
| Gupshup | BSP oficial | endpoint passthrough `/partner/app/{APP_ID}/v3/message` aceita e devolve formato Meta | [passthrough](https://partner-docs.gupshup.io/docs/whatsapp-passthrough-apis-for-partners) |
| Twilio | BSP oficial | Programmable Messaging com endereços `whatsapp:+E164`; templates pela Content API; webhook de entrada em form-encoded; `X-Twilio-Signature` = HMAC-SHA1 da URL + parâmetros ordenados, com o auth token | [WhatsApp](https://www.twilio.com/docs/whatsapp/api), [segurança](https://www.twilio.com/docs/usage/webhooks/webhooks-security) |
| Evolution API | gateway open source (Apache-2.0, ~9,8k ★) | backend Baileys (WhatsApp Web) **ou** Cloud API oficial; integra com Typebot, Chatwoot, n8n | [repo](https://github.com/EvolutionAPI/evolution-api), [docs](https://doc.evolution-api.com/v2/en/get-started/introduction) |
| Z-API | não oficial (Brasil) | sessão do WhatsApp Web via QR code | [docs](https://developer.z-api.io/en/quickstart/introduction) |

## Conexões não oficiais

- Os Termos do WhatsApp proíbem mensagens em massa ou automáticas e acesso por meios automatizados ou software não autorizado ([termos](https://www.whatsapp.com/legal/terms-of-service)).
- O Baileys avisa que não é afiliado ao WhatsApp e pede para evitar mensagens em massa ou automatizadas ([Baileys](https://github.com/WhiskeySockets/Baileys)); usuários do whatsmeow relatam avisos de conta em risco ([issue](https://github.com/tulir/whatsmeow/issues/810)).
- Regra do ciclo: adapters Baileys, whatsmeow e Z-API têm `official: false`, ficam fora de produção por padrão e só entram com ADR que registre o risco aceito.
- Evolution API com backend Cloud API é oficial no envio; com backend Baileys, não.

## Escolha do adapter

| Situação | Adapter |
|---|---|
| Padrão | `MetaCloudCompatibleAdapter` configurado para Meta direto |
| Cliente já tem conta na 360dialog ou Gupshup | mesmo adapter, outra configuração |
| Cliente já usa Twilio | `TwilioAdapter` (skills do plugin `twilio-developer-kit`) |
| Ambiente interno de testes sem conta Meta | `EvolutionAdapter` com `official: false`, em número separado |
