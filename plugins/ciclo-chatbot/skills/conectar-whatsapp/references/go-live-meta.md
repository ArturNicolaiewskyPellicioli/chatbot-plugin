# Checklist de go-live na Meta

Conferido em 2026-10-06. Fonte principal: [Get started](https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started).

## Contas e app
- [ ] Portfólio empresarial (Business Manager) da empresa dona do número.
- [ ] Verificação da empresa iniciada ou concluída (libera mais números, mais templates e as faixas maiores de limite).
- [ ] App Meta do tipo Business com o caso de uso de WhatsApp ("Connect with customers through WhatsApp").
- [ ] WhatsApp Business Account (WABA) ligada ao portfólio.
- [ ] Forma de pagamento na WABA (cobrança por mensagem; ver [preços](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing)).

## Número
- [ ] Número que pode receber SMS ou ligação para verificação e que não está em uso no app WhatsApp (ou seguir o caminho Coexistence).
- [ ] Nome de exibição aprovado (`name_status` = APPROVED).
- [ ] Registro do número com PIN de verificação em duas etapas.
- [ ] Limite de números: portfólios novos registram 2; 20 após verificação ou ao atingir a faixa de 2.000 ([phone numbers](https://developers.facebook.com/documentation/business-messaging/whatsapp/business-phone-numbers/phone-numbers)).

## Acesso
- [ ] Usuário do sistema no portfólio, com token permanente e permissões `business_management`, `whatsapp_business_messaging`, `whatsapp_business_management` (somente as necessárias).
- [ ] Token e app secret no cofre de segredos de produção; staging com credenciais próprias.

## Webhook
- [ ] URL de callback do app apontando para `/webhooks/meta/<appRef>` (a Meta envia todos os números do app para ela; override por WABA ou número só se necessário: [override](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/override/)).
- [ ] URL HTTPS de produção com certificado válido ([getting started](https://developers.facebook.com/docs/graph-api/webhooks/getting-started)).
- [ ] Verify token de produção configurado e handshake confirmado ([endpoint](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/create-webhook-endpoint)).
- [ ] Campo `messages` assinado na WABA (e `smb_message_echoes` em Coexistence).
- [ ] Assinatura `X-Hub-Signature-256` validada com o app secret de produção.
- [ ] App em modo Live.

## Templates
- [ ] Templates de utility para retornos fora da janela de 24h (ex.: "seu atendimento foi retomado") e de marketing apenas com opt-in ([templates](https://developers.facebook.com/documentation/business-messaging/whatsapp/templates/overview)).
- [ ] Sincronização de status de templates ativa (APPROVED, REJECTED, PAUSED).

## Limites e qualidade
- [ ] Faixa inicial de limite de mensagens conhecida (começa em 250 usuários únicos por 24h fora da janela de serviço) ([messaging limits](https://developers.facebook.com/documentation/business-messaging/whatsapp/messaging-limits)).
- [ ] Monitoramento da qualidade do número (GREEN, YELLOW, RED).

## Teste final
- [ ] Mensagem real de um celular pessoal → resposta do bot em produção.
- [ ] Status `delivered` e `read` gravados; custo registrado a partir do campo de preço do status.
- [ ] Mensagem com mídia (se o bot aceitar) processada.
- [ ] Opt-out testado ("parar", "sair") se houver mensagens proativas.

## SaaS multi-tenant: Embedded Signup
- [ ] Tech Provider ou Solution Partner.
- [ ] Embedded Signup **v4** (a v2 deixa de funcionar em 2026-10-15); fluxo devolve WABA ID, phone number ID e um código trocado por token do negócio ([embedded signup](https://developers.facebook.com/documentation/business-messaging/whatsapp/embedded-signup/overview/)).
- [ ] Limite de onboarding: 10 empresas por semana, 200 após verificação da empresa, App Review e Access Verification (mesma fonte).
- [ ] Cada cliente vira um `tenant` com suas `channel_accounts`; tokens por cliente no cofre.

## Coexistence (número que segue no app WhatsApp Business)
- [ ] App WhatsApp Business 2.24.17 ou superior; sincronização de histórico em até 24h.
- [ ] Vazão fixa de 20 mensagens/s; mensagens temporárias, visualização única, localização em tempo real e listas de transmissão desligadas.
- [ ] Webhook `smb_message_echoes` tratado para registrar o que o humano enviou pelo app.
- Fonte: [Coexistence](https://developers.facebook.com/documentation/business-messaging/whatsapp/embedded-signup/onboarding-business-app-users/).
