---
name: conectar-whatsapp
description: Conecta o chatbot publicado ao WhatsApp pela API oficial da Meta, do app de desenvolvimento com número de teste até o número real em produção, cobrindo app Meta, portfólio, verificação da empresa, WABA, registro do número, nome de exibição, usuário do sistema com token permanente, webhook assinado, templates, Embedded Signup v4 para SaaS multi-tenant e Coexistence, com teste de ida e volta real. Usar quando o usuário disser "conectar no WhatsApp", "número de teste", "token permanente", "configurar webhook na Meta", "colocar o número em produção", "Embedded Signup", "coexistence", ou na fase 10 do /ciclo-chatbot:iniciar.
argument-hint: "[teste | producao | embedded-signup | coexistence]"
---

# Conexão com o WhatsApp (Meta)

Checklist completo, com fontes, em `${CLAUDE_SKILL_DIR}/references/go-live-meta.md`.

## Regras

- O usuário faz login e digita senhas, códigos de verificação e dados da empresa. Claude nunca pede nem guarda essas informações no chat.
- Tokens e app secret vão direto para o cofre de segredos do PaaS, por ambiente, e nunca para arquivo, banco ou log.
- Se as ferramentas do Claude in Chrome estiverem disponíveis e o usuário quiser, guiar a navegação no painel da Meta passo a passo, parando a cada tela que pedir decisão ou credencial. Sem elas, dar o passo a passo em texto.
- Conferir no [changelog da Cloud API](https://developers.facebook.com/documentation/business-messaging/whatsapp/changelog) se algo mudou no onboarding antes de começar.

## Modos

- `teste` (usado na fatia 0 da implementação): app Meta de desenvolvimento, número de teste, até 5 destinatários verificados, webhook apontando para o túnel local ou para staging.
- `producao`: número real, verificação da empresa, token permanente, webhook de produção, templates. É o portão da fase 10.
- `embedded-signup`: para SaaS que conecta números de clientes. Construir na v4; a v2 deixa de funcionar em 2026-10-15.
- `coexistence`: número que continua no app WhatsApp Business; vazão fixa de 20 mensagens/s e alguns recursos desligados.

## Passos do modo `producao`

1. Percorrer `go-live-meta.md` item por item com o usuário, marcando o que já existe.
2. Cadastrar a conta em `channel_accounts` (provider `meta`, `provider_app_ref` = app Meta que assina os webhooks, `external_account_id` = phone_number_id, `business_portfolio_id`, `credentials_ref` = nome do segredo).
3. Configurar o webhook de produção (URL HTTPS, verify token, assinar o campo `messages`), confirmar o handshake e a validação de assinatura.
4. Submeter os templates definidos na descoberta e aguardar aprovação.
5. Teste de ida e volta: o usuário manda uma mensagem de um celular pessoal; conferir resposta, status `delivered` e `read` gravados, trace no Langfuse e ausência de erros no Sentry.
6. Registrar faixa de limite de mensagens, qualidade do número e forma de pagamento configurada em `docs/chatbot/10-go-live.md`.
7. Rodar o checklist da fase 10 e apresentar o portão.
