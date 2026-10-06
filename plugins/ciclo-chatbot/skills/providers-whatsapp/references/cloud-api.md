# WhatsApp Cloud API: fatos com fonte

Conferido em 2026-10-06. A documentação mudou de `/docs/whatsapp/...` para `/documentation/business-messaging/whatsapp/...`; algumas páginas antigas ainda mostram versões velhas nos exemplos. Itens marcados com ⚠ mudaram em 2025-2026 e afetam o desenho.

## Versões
- A versão mais recente da Graph API em 2026-10-06 é a v26.0 (2026-07-29); cada versão expira cerca de dois anos depois (v25.0 até 2028-07-29). Deixar a versão em configuração ([versões](https://developers.facebook.com/docs/graph-api/changelog/versions/)).
- A On-Premises API foi desligada em 2025-10-23; só existe a Cloud API ([sunset](https://developers.facebook.com/docs/whatsapp/on-premises/sunset)).

## Envio
- `POST https://graph.facebook.com/{versão}/{PHONE_NUMBER_ID}/messages` com `messaging_product: "whatsapp"`, `to` (ou `recipient`, ver BSUID) e `type` ([messages](https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages)).
- Tipos: texto, imagem, vídeo, áudio, documento, figurinha, localização, endereço, contatos, interativos (botões, lista, pedido de localização, CTA URL, flows), reação, template ([enviar mensagens](https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/send-messages)).
- Texto: até 4.096 caracteres ([texto](https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/text-messages)).
- Botões de resposta: até 3, título até 20 caracteres. Lista: até 10 seções e 10 linhas no total, título da linha até 24 caracteres ([botões](https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/interactive-reply-buttons-messages), [listas](https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/interactive-list-messages)).
- Marcar como lida + digitando, na mesma chamada: `{"messaging_product":"whatsapp","status":"read","message_id":"<wamid>","typing_indicator":{"type":"text"}}`. O indicador some ao responder ou após 25 s ([typing indicators](https://developers.facebook.com/documentation/business-messaging/whatsapp/typing-indicators)).

## Webhooks
- Verificação: GET com `hub.mode=subscribe`, `hub.verify_token` e `hub.challenge`; conferir o token e responder 200 com o `challenge` ([criar endpoint](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/create-webhook-endpoint)).
- Assinatura: header `X-Hub-Signature-256: sha256=<HMAC-SHA256 do corpo bruto com o app secret>`. Validar contra os bytes originais, antes de qualquer parse.
- Formato: `object: "whatsapp_business_account"` → `entry[].changes[].value` com `metadata.phone_number_id`, `contacts`, `messages` ou `statuses`. Até 1.000 atualizações por lote, até 3 MB ([webhooks](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/overview)).
- Reenvio: qualquer resposta diferente de 200 é reenviada com frequência decrescente por até 7 dias, e "esses reenvios podem gerar notificações duplicadas". Responder 200 rápido e processar de forma assíncrona (mesma fonte).
- HTTPS com certificado válido; certificado autoassinado não é aceito ([getting started](https://developers.facebook.com/docs/graph-api/webhooks/getting-started)).
- Status possíveis: `sent`, `delivered`, `read`, `played`, `failed`; `delivered` pode não chegar quando `read` chega ([status](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages/status/)).

## ⚠ Identidade do usuário: BSUID e usernames
- Desde cerca de abril de 2026, webhooks trazem `user_id`, um ID do usuário com escopo do negócio (BSUID). Quando o usuário adota um username, `wa_id` e `from` podem não vir. Desde julho de 2026 é possível enviar para um BSUID pelo campo `recipient`. A Meta diz que o suporte é obrigatório para parceiros e empresas integradas diretamente ([BSUID](https://developers.facebook.com/documentation/business-messaging/whatsapp/business-scoped-user-ids/)).
- Consequência: a chave do contato é `bsuid` ou telefone, por conta; nunca só telefone.

## Janela de atendimento e templates
- Janela de 24h a partir de cada mensagem (ou ligação) do usuário; fora dela, só template ([enviar mensagens](https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/send-messages)).
- Categorias de template: marketing, utility, authentication. Revisão em até 24h; status como APPROVED, REJECTED, PAUSED. Limites: 250 templates por WABA sem verificação, 6.000 com verificação; 100 criados por hora ([templates](https://developers.facebook.com/documentation/business-messaging/whatsapp/templates/overview)).

## ⚠ Preços
- Cobrança por mensagem entregue desde 2025-07-01; faixas de volume contadas por portfólio ([pricing](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing)).
- A Meta anuncia que, a partir de 2026-10-01, cobra também mensagens de serviço e utility dentro da janela, com a tarifa de utility do mercado ([mensagens sem template](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing/non-template-messages)). Em 2026-10-06 a página ainda mostrava aviso de "upcoming": confirmar na fatura.
- Entradas por anúncio click-to-WhatsApp e CTA de Página ainda abrem janela gratuita de 72h (mesma fonte de pricing).
- O status traz `pricing` (categoria e se é cobrável): gravar para custo por conversa.

## ⚠ Limites
- Limites de mensagens por portfólio desde 2025-10-08: 250 → 2.000 → 10.000 → 100.000 → ilimitado usuários únicos por 24h móveis; só contam mensagens fora da janela de serviço ([messaging limits](https://developers.facebook.com/documentation/business-messaging/whatsapp/messaging-limits)).
- Vazão: 80 mensagens/s por número por padrão, com upgrade automático até 1.000; números em Coexistence ficam em 20/s. Erro 130429 = acima da vazão ([throughput](https://developers.facebook.com/documentation/business-messaging/whatsapp/throughput)).
- Par empresa-usuário: 1 mensagem a cada 6 s; rajadas até 45 em 6 s exigem pausa equivalente. Erro 131056. Retentativa com backoff exponencial 4^X. Chamadas à Graph API limitadas a 5.000/h por WABA ativa ([about the platform](https://developers.facebook.com/documentation/business-messaging/whatsapp/about-the-platform)).
- Qualidade do número: GREEN, YELLOW, RED; afeta a subida de faixa ([phone numbers](https://developers.facebook.com/documentation/business-messaging/whatsapp/business-phone-numbers/phone-numbers)).

## Mídia
- `GET /{MEDIA_ID}` devolve uma URL que expira em 5 minutos; baixar com o token Bearer. IDs de mídia recebida valem 7 dias; mídia enviada, 30 dias. Desde 2025-10-16, webhooks de mídia recebida já trazem a URL ([media](https://developers.facebook.com/documentation/business-messaging/whatsapp/business-phone-numbers/media)).
- Limites: imagem 5 MB, áudio e vídeo 16 MB, documento 100 MB, figurinha WebP 100–500 KB (mesma fonte).
- Consequência: copiar a mídia para storage próprio no worker logo ao receber.

## Onboarding (detalhes na fase 10)
- App Meta do tipo Business com o caso de uso de WhatsApp → portfólio → WABA → número → webhook → usuário do sistema com token permanente e permissões `business_management`, `whatsapp_business_messaging`, `whatsapp_business_management` ([get started](https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started)).
- ⚠ Embedded Signup (SaaS que conecta números de clientes): a v2 será descontinuada em 2026-10-15; construir na v4 ([embedded signup](https://developers.facebook.com/documentation/business-messaging/whatsapp/embedded-signup/overview/)).
- Coexistence: app WhatsApp Business e Cloud API no mesmo número, 20 mensagens/s, alguns recursos desligados, webhook `smb_message_echoes` para espelhar o que foi enviado pelo app ([coexistence](https://developers.facebook.com/documentation/business-messaging/whatsapp/embedded-signup/onboarding-business-app-users/)).

## ⚠ Política para bots de IA
- Os [WhatsApp Business Solution Terms](https://www.whatsapp.com/legal/business-solution-terms) (vigentes desde 2026-03-06) proíbem provedores de IA quando a IA é a funcionalidade principal oferecida (assistentes de uso geral), com exceções para usuários do EEE e do Brasil; bots que atendem clientes do próprio negócio seguem permitidos. Os termos também proíbem usar dados da plataforma para criar, treinar ou melhorar sistemas de IA, salvo fine-tuning para uso interno exclusivo. Contexto: a regra valeu para todos a partir de 2026-01-15 ([TechCrunch](https://techcrunch.com/2025/10/18/whatssapp-changes-its-terms-to-bar-general-purpose-chatbots-from-its-platform)).
- Brasil: o CADE impôs medida preventiva contra a regra e, em 2026-04-23, manteve multa diária de R$ 250 mil por descumprimento, considerando a cobrança por mensagens de chatbots uma barreira de entrada ([CADE](https://www.gov.br/cade/pt-br/assuntos/noticias/cade-mantem-multa-diaria-contra-meta-e-whatsapp-por-descumprimento-de-medida-preventiva)). O changelog da Meta registra cobrança específica para "AI Providers" em mensagens sem template, retirada na UE/EEE em 2026-05-13 ([changelog](https://developers.facebook.com/documentation/business-messaging/whatsapp/changelog)). Nada disso se aplica a bots de atendimento de um negócio; conferir o estado na data.
- Política geral de mensagens (opt-in, setores proibidos): [WhatsApp Business Messaging Policy](https://whatsappbusiness.com/policy/).

## SDKs
- O SDK Node.js oficial da Meta está arquivado ([repo](https://github.com/WhatsApp/WhatsApp-Nodejs-SDK)).
- TypeScript (MIT, ativos em 2026-09): `whatsapp-api-js`, `@great-detail/whatsapp`. Python: `pywa` (MIT, valida assinatura) ([pywa](https://github.com/david-lev/pywa)).
- O adapter usa poucos endpoints; um cliente HTTP próprio dentro do adapter evita prender o núcleo a um SDK.
