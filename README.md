# ciclo-chatbot-marketplace

Marketplace de plugins do Claude Code para criar chatbots com IA no WhatsApp.

| Plugin | O que faz |
|---|---|
| [`ciclo-chatbot`](plugins/ciclo-chatbot) | Orquestra o ciclo completo: descoberta, arquitetura, banco escalável, IA, providers modulares de WhatsApp, implementação, testes, segurança, deploy, conexão com a Meta e operação |
| [`ciclo-chatbot-essenciais`](plugins/ciclo-chatbot-essenciais) | Opcional: instala de uma vez as peças núcleo da comunidade |

## Instalar no Claude Code

No Claude Code:

```
/plugin marketplace add ArturNicolaiewskyPellicioli/chatbot-plugin
/plugin install ciclo-chatbot@ciclo-chatbot-marketplace
/plugin install ciclo-chatbot-essenciais@ciclo-chatbot-marketplace
```

Para testar localmente a partir de um clone: `/plugin marketplace add ./caminho/para/o/clone`.

## Instalar no Cowork

Compacte o conteúdo de `plugins/ciclo-chatbot` em um arquivo `ciclo-chatbot.plugin` e instale pelo app.

## Validar

```
claude plugin validate .
claude plugin validate plugins/ciclo-chatbot --strict
```
