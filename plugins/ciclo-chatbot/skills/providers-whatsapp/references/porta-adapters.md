# Porta e adapters de providers

Arquitetura hexagonal: o núcleo depende da porta; cada provider é um adapter. Referências de mercado para o mesmo problema: o `@chat-adapter/whatsapp` do Vercel Chat SDK (adapter normalizado para a Cloud API, MIT, [vercel/chat](https://github.com/vercel/chat)) e os serviços por provider do Chatwoot em `app/services/whatsapp/providers/` (MIT, [chatwoot](https://github.com/chatwoot/chatwoot)).

## Um adapter, três providers oficiais

Meta direto, 360dialog e Gupshup (endpoint passthrough v3) usam o formato de payload e webhook da Meta. Um único `MetaCloudCompatibleAdapter`, configurado com `{ baseUrl, authHeader, signatureHeader, graphVersion }`, atende os três. Twilio e Evolution API têm formatos próprios e ganham adapters próprios. Detalhes em `providers.md`.

## Porta (TypeScript)

```ts
export interface MessagingProvider {
  readonly id: ProviderId;                     // 'meta' | '360dialog' | 'gupshup' | 'twilio' | 'evolution' | 'zapi'
  readonly capabilities: Capabilities;

  /** Handshake GET (Meta: hub.challenge). Devolve null se não for um handshake. */
  verifyHandshake?(req: HandshakeRequest, app: ProviderApp): HandshakeResponse | null;
  /** Sempre sobre o corpo bruto, com o segredo do app do provider e comparação em tempo constante. */
  verifySignature(rawBody: Buffer, headers: Headers, url: string, app: ProviderApp): boolean;
  /** Um webhook pode trazer várias mensagens e status, de vários números do mesmo app. */
  parseWebhook(rawBody: Buffer, headers: Headers): NormalizedEvent[];

  send(account: ChannelAccount, to: Recipient, content: OutboundContent,
       opts?: { replyTo?: string; idempotencyKey?: string }): Promise<SendResult>;
  markRead?(account: ChannelAccount, providerMessageId: string, typing?: boolean): Promise<void>;
  downloadMedia(account: ChannelAccount, ref: MediaRef): Promise<NodeJS.ReadableStream>;
  templates?: {
    list(account: ChannelAccount): Promise<TemplateInfo[]>;
    send(account: ChannelAccount, to: Recipient, name: string, lang: string, params: TemplateParams): Promise<SendResult>;
  };
}

export type Capabilities = {
  official: boolean;               // false = conexão via WhatsApp Web (Baileys, Z-API)
  templates: boolean;
  replyButtons: number;            // 3 na Cloud API; 0 se não suportar
  listRows: number;                // 10 na Cloud API
  reactions: boolean;
  typingIndicator: boolean;
  readReceipts: boolean;
  bsuid: boolean;
  maxMessagesPerSecond: number;    // 80 por padrão na Cloud API; 20 em Coexistence
  mediaMaxBytes: Record<'image' | 'video' | 'audio' | 'document', number>;
  signature: 'hmac-sha256' | 'hmac-sha1' | 'apikey' | 'none';
};

/** App ou conta do provider que assina os webhooks (Meta: um app com um app secret, que pode
 *  atender vários números; Twilio: uma conta com um auth token). channel_accounts.provider_app_ref aponta para ele. */
export type ProviderApp = { provider: ProviderId; ref: string; webhookSecretRef: string; verifyTokenRef?: string };

export type Recipient = { phone?: string; bsuid?: string };   // pelo menos um

export type NormalizedEvent = InboundMessage | StatusEvent;

export type InboundMessage = {
  kind: 'message';
  provider: ProviderId;
  externalAccountId: string;       // phone_number_id, instância etc.
  providerMessageId: string;
  from: { phone?: string; bsuid?: string; username?: string; name?: string };
  timestamp: Date;
  type: 'text' | 'media' | 'interactive_reply' | 'location' | 'reaction' | 'contacts' | 'unsupported';
  text?: string;
  media?: { ref: MediaRef; mime: string; caption?: string };
  reply?: { id: string; title: string };
  contextProviderMessageId?: string;
  raw: unknown;                    // só para debug e reprocessamento
};

export type StatusEvent = {
  kind: 'status';
  provider: ProviderId;
  externalAccountId: string;
  providerMessageId: string;
  status: 'sent' | 'delivered' | 'read' | 'played' | 'failed';
  timestamp: Date;
  error?: { code: string; title: string };
  billable?: boolean;
  pricingCategory?: string;
  raw: unknown;
};

export type NormalizedError =
  | { type: 'RateLimited'; retryAfterMs?: number }        // Meta 130429
  | { type: 'PairRateLimited'; retryAfterMs?: number }    // Meta 131056
  | { type: 'OutsideServiceWindow' }                      // precisa de template
  | { type: 'TemplateRejectedOrPaused' }
  | { type: 'InvalidRecipient' }
  | { type: 'Auth' }                                      // token expirado ou revogado
  | { type: 'Transient' }                                 // 5xx, timeout
  | { type: 'Permanent'; code: string };
```

Em Python, a mesma porta vira um `typing.Protocol` com dataclasses (ou modelos Pydantic) para os eventos. Os nomes de campos e tipos de erro devem ser idênticos entre linguagens para os testes de contrato serem portáveis.

## Pipeline de webhook

```
POST /webhooks/:provider/:appRef     (GET na mesma rota para o handshake)
 1. ler o corpo bruto (sem parser JSON antes)
 2. carregar o ProviderApp por (provider, appRef); 404 se não existir
 3. adapter.verifySignature(raw, headers, url, app); 401 se falhar (logar sem o corpo)
 4. adapter.parseWebhook(raw) → eventos
 5. para cada evento, resolver a channel_account por (provider, externalAccountId)
    (Meta: metadata.phone_number_id) e conferir que ela pertence a este app;
    se não pertencer ou não existir, descartar o evento e registrar alerta
 6. INSERT em inbound_events ... ON CONFLICT DO NOTHING (um por evento)
 7. enfileirar os IDs inseridos
 8. responder 200
```

- Nada de LLM, banco de negócio ou chamada ao provider entre 1 e 8.
- A Meta envia os webhooks de todos os números para a URL de callback do app; o segredo de assinatura é do app, não do número. Por isso a rota identifica o app e a conta é resolvida por evento. Se precisar de URL por WABA ou por número, a Meta permite sobrescrever o callback ([webhook override](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/override/)); a validação do passo 5 continua necessária.
- Um job varre `inbound_events` não processados e reenfileira (recupera falhas do Redis).

## Uma conversa por vez

Quando o contato manda duas ou três mensagens seguidas, workers em paralelo gerariam respostas duplicadas e bateriam no limite de 1 mensagem a cada 6 s por destinatário (erro 131056).
- Serializar o processamento por conversa: lock de transação no Postgres (`pg_advisory_xact_lock` com um hash do `conversation_id`, compatível com PgBouncer em modo transação) ou fila com concorrência 1 por chave de conversa, conforme o ADR de fila.
- Debounce curto (ex.: 1 a 3 s, ajustado nas evals): o job espera a rajada terminar e processa as mensagens juntas, gerando uma única resposta. Conferir na documentação da fila escolhida o recurso equivalente (deduplicação ou atraso por chave).

## Serviços do núcleo (agnósticos de provider)

| Serviço | Responsabilidade |
|---|---|
| Inbox | deduplicação por `(provider, provider_event_id)` e reprocessamento |
| Identidade | resolve ou cria `contacts` + `contact_channels` por telefone ou BSUID; une os dois quando chegarem juntos |
| Janela de 24h | atualiza `contact_channels.last_inbound_at` a cada mensagem recebida; decide texto livre ou template |
| Limitador de vazão | balde de tokens por número (capacidade do adapter) + 1 mensagem a cada 6 s por destinatário; junta pedaços de resposta numa mensagem |
| Envio | via outbox; retentativa por tipo de `NormalizedError` (backoff exponencial para limites e transitórios; sem retentativa para permanentes) |
| Status | aplica status só para frente; grava eventos e custo |
| Mídia | baixa e copia para storage próprio assim que a mensagem chega |
| Templates | sincroniza `message_templates`; escolhe template quando a janela fechou |
| Capacidades | se `listRows = 0`, transforma lista em menu numerado; se `replyButtons = 0`, em opções em texto |
| Custo | soma `billable` por tenant e conversa |

## Roteamento e dois providers ao mesmo tempo

- `channel_accounts` liga cada número a exatamente um provider. Roteamento padrão: por número.
- Trocar o provider de um número: atualizar a linha existente de `channel_accounts` (provider, app, identificador externo, credencial), mantendo o `id` e o histórico; detalhes em `modelar-banco/references/modelo-referencia.md`.
- Dois providers simultâneos, casos seguros:
  - números diferentes para finalidades diferentes (ex.: produção na Cloud API, número interno de testes na Evolution);
  - migração gradual de um provider oficial para outro, número a número.
- Failover para outro número muda o remetente e a janela de 24h é por número: o número reserva só consegue mandar templates para quem não falou com ele. Failover só entre contas oficiais e por decisão explícita, nunca automático e silencioso.
- Adapters com `official: false` nunca recebem tráfego de produção sem decisão registrada em ADR (risco de banimento do número).

## Testes de contrato

Para cada adapter, uma pasta de fixtures com payloads reais anonimizados e o resultado normalizado esperado. Os mesmos casos de comportamento (duplicata, status fora de ordem, sem telefone, assinatura inválida, lote com mensagens e status misturados, evento de um número que não pertence ao app da rota) rodam contra todos os adapters.
