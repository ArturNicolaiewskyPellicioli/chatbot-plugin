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
/plugin marketplace add anthropics/claude-plugins-official
/plugin install ciclo-chatbot@ciclo-chatbot-marketplace
/plugin install ciclo-chatbot-essenciais@ciclo-chatbot-marketplace
```

O marketplace oficial (`claude-plugins-official`) é necessário para o `ciclo-chatbot-essenciais`, cujas dependências vêm dele. Se ele já estiver adicionado, o segundo comando pode ser pulado.

Para testar localmente a partir de um clone: `/plugin marketplace add ./caminho/para/o/clone`.

## Usar no Claude Code na web (sessões na nuvem)

O comando `/plugin` não está disponível nas sessões na nuvem. Declare os plugins no `.claude/settings.json` do repositório do projeto, e cada nova sessão os instala ao iniciar:

```json
{
  "extraKnownMarketplaces": {
    "ciclo-chatbot-marketplace": {
      "source": { "source": "github", "repo": "ArturNicolaiewskyPellicioli/chatbot-plugin" }
    },
    "claude-plugins-official": {
      "source": { "source": "github", "repo": "anthropics/claude-plugins-official" }
    }
  },
  "enabledPlugins": {
    "ciclo-chatbot@ciclo-chatbot-marketplace": true,
    "ciclo-chatbot-essenciais@ciclo-chatbot-marketplace": true
  }
}
```

## Instalar no Cowork

Compacte o conteúdo de `plugins/ciclo-chatbot` em um arquivo `ciclo-chatbot.plugin` e instale pelo app.

## Validar

```
claude plugin validate .
claude plugin validate plugins/ciclo-chatbot --strict
```
