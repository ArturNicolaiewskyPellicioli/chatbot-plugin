# ciclo-chatbot

Plugin para Claude Code (e Cowork) que conduz a criação de um chatbot com IA conectado ao WhatsApp, da descoberta e do desenho do banco até a publicação, a conexão com a API oficial da Meta e a operação. Em cada fase, ele orquestra as peças da comunidade mais adotadas para aquele trabalho e completa com material próprio, com fontes primárias.

## Como usar

```
/ciclo-chatbot:iniciar meu-bot
```

O orquestrador cria `.ciclo-chatbot/estado.md` no projeto, prepara o ambiente e segue fase por fase, parando em um portão de aprovação ao fim de cada uma. Dá para retomar em outra sessão (um hook lembra a fase atual) ou chamar uma fase isolada, por exemplo `/ciclo-chatbot:modelar-banco revisar prisma/schema.prisma`.

| # | Fase | Skill |
|---|---|---|
| 0 | Ambiente | `preparar-ambiente` |
| 1 | Descoberta | `descoberta` |
| 2 | Arquitetura e stack (matriz de decisão por projeto) | `decidir-stack` |
| 3 | Banco de dados | `modelar-banco` |
| 4 | Camada de IA | `camada-ia` |
| 5 | Providers WhatsApp (ports and adapters) | `providers-whatsapp` |
| 6 | Implementação em fatias | `implementar` |
| 7 | Testes e evals | `testes-e-evals` |
| 8 | Segurança e LGPD | `auditoria-seguranca` |
| 9 | Publicação em PaaS | `publicar` |
| 10 | Conexão com a Meta | `conectar-whatsapp` |
| 11 | Operação | `operar` |

## Como a comunidade entra

Modelo híbrido: as skills deste plugin decidem o fluxo, os portões e o que é específico de chatbot de WhatsApp; o trabalho especializado é delegado a plugins, skills, agentes e MCPs da comunidade, invocados pelo nome. Nada é copiado deles.

Exemplo, fase de banco: regras do `postgres-best-practices` (Supabase) e do `pg-aiguide` (TigerData) alimentam o agente `arquiteto-dados`; o schema é revisado em paralelo pelo `revisor-banco` deste plugin e pelo `database-architect` do wshobson; o Squawk roda automaticamente em cada migração; o modelo é validado num Postgres real com volume projetado e, opcionalmente, pelo Postgres MCP Pro.

O catálogo completo (o que entra em cada fase, comandos de instalação, licenças, o que ficou de fora e por quê) está em [`skills/preparar-ambiente/references/catalogo-comunidade.md`](skills/preparar-ambiente/references/catalogo-comunidade.md). A skill `preparar-ambiente` instala só o que cada fase precisa.

## Componentes

| Tipo | Itens |
|---|---|
| Skills | 13 (orquestrador + 12 fases) |
| Agentes | `arquiteto-dados`, `revisor-banco`, `engenheiro-ia`, `especialista-whatsapp`, `revisor-modularidade`, `auditor-seguranca`, `engenheiro-deploy` |
| Hooks | `SessionStart` (retoma o ciclo), `PostToolUse` (Squawk em migrações `.sql`) |
| MCPs | Context7 (documentação atualizada de bibliotecas), Langfuse Docs |

## Requisitos

- Claude Code com shell no repositório do projeto. Sem terminal (Cowork sem computador vinculado), as fases de desenho funcionam; instalação de plugins, validação do banco, implementação e deploy precisam de terminal.
- `python3` para os hooks (sem ele, os hooks apenas não rodam).
- Opcional: `squawk-cli` (`npm i -g squawk-cli`) para o lint automático de migrações.
- Nenhuma variável de ambiente é obrigatória para instalar. Credenciais de banco, Meta, LLM e PaaS são configuradas por fase, fora do repositório.

## Decisões de base

- WhatsApp Cloud API oficial como provider padrão, atrás de uma porta `MessagingProvider`: dá para trocar de provider ou usar dois ao mesmo tempo (360dialog, Gupshup, Twilio, Evolution API), com roteamento por número.
- PostgreSQL (18 quando disponível) com pgvector; Redis para fila; monólito modular com processos `web` e `worker`.
- Stack decidida por projeto com matriz e ADRs.
- PaaS por padrão (Railway, Render ou Fly.io).
- Código sem funções duplicadas, verificado por ferramenta e por revisor dedicado a cada fatia.

## Atualidade

Fatos de plataformas (Meta, PaaS, modelos de LLM) foram conferidos em 2026-10-06 nas fontes oficiais citadas em cada referência. As skills mandam reconferir fatos voláteis na hora de usar. O modelo de dados de referência foi testado em PostgreSQL 18.6 com pgvector 0.8.7 e Squawk 2.67.

## Licença

MIT. As peças da comunidade seguem as licenças dos seus autores (ver catálogo).
