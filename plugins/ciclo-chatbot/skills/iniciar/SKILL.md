---
name: iniciar
description: Orquestra o ciclo completo de um chatbot com IA conectado ao WhatsApp, da descoberta e do desenho do banco até a publicação em PaaS, a conexão com a API oficial da Meta e a operação, chamando em cada fase as melhores skills, agentes e MCPs da comunidade, com portões de aprovação e estado salvo no projeto. Usar quando o usuário disser "/ciclo-chatbot:iniciar", "criar um chatbot com IA", "bot de WhatsApp com IA", "novo projeto de chatbot", "continuar o ciclo do chatbot", "em que fase estamos" ou pedir o fluxo inteiro.
argument-hint: "[nome do projeto | número ou nome da fase para retomar]"
---

# Ciclo Chatbot: orquestrador

Conduzir o projeto pelas fases abaixo, uma de cada vez. Cada fase tem uma skill deste plugin que sabe quais peças da comunidade chamar e o que entregar. Esta skill não faz o trabalho das fases: ela mantém o estado, chama a skill certa e aplica os portões.

## Princípios (valem para todas as fases)

1. **O banco é o coração.** Nenhuma linha de código de domínio antes do modelo de dados aprovado e validado com volume projetado.
2. **Código modular, sem função duplicada.** Antes de criar uma função, procurar se ela já existe. Duplicação é bloqueio de portão, não sugestão.
3. **Fonte séria para toda afirmação técnica.** Usar documentação oficial, RFCs e repositórios dos mantenedores, e registrar a URL no artefato. Fatos que mudam (preços, versão da Graph API, limites, modelos de LLM) são conferidos na hora com o MCP Context7 ou WebFetch, nunca de memória.
4. **Comunidade primeiro, sem sobreposição.** Se a peça da comunidade indicada estiver instalada, usá-la. Se não estiver, oferecer instalar (`ciclo-chatbot:preparar-ambiente`) ou seguir o material de apoio deste plugin, e dizer ao usuário qual caminho foi usado. Nunca rodar duas peças que fazem a mesma coisa na mesma tarefa (por exemplo, dois revisores de código genéricos). Exceção deliberada: revisores independentes em paralelo quando usam métodos diferentes e não veem a opinião um do outro (como os dois revisores do banco).
5. **Núcleo agnóstico de provider.** Só os adapters conhecem o formato de cada provider de WhatsApp.
6. **Portões explícitos.** Ao fim de cada fase, apresentar o portão e esperar aprovação. Sem aprovação, não avançar.

Nomes de skills e agentes da comunidade podem mudar entre versões. Antes de invocar um, conferir a lista de skills e agentes disponíveis na sessão e usar o identificador exato que aparece lá.

## Passo 0: estado

1. Procurar `.ciclo-chatbot/estado.md` na raiz do projeto.
   - Se existir: ler, dizer em duas linhas onde o projeto está e continuar da fase atual, ou da fase pedida em `$ARGUMENTS`.
   - Se não existir: criar a partir de `${CLAUDE_SKILL_DIR}/references/estado-template.md`, com o nome do projeto (de `$ARGUMENTS` ou perguntado) e a data de hoje.
2. Confirmar o ambiente. O ideal é Claude Code com shell no repositório do projeto. Sem shell (Cowork sem computador vinculado), as fases 1, 2, 4 e 5 e o desenho da fase 3 funcionam; a instalação de plugins (fase 0), a validação do banco (Postgres local, Squawk, `EXPLAIN`) e as fases 6 a 10 precisam de terminal. Avisar o usuário e seguir com o que for possível.

## Passo 1: ambiente

Se o estado não marca a fase 0 como concluída, invocar `ciclo-chatbot:preparar-ambiente`. Ela instala o núcleo e, conforme as fases e a stack, as peças específicas.

## Fases

| # | Fase | Skill deste plugin | Peças principais da comunidade | Artefato |
|---|---|---|---|---|
| 0 | Ambiente | `preparar-ambiente` | superpowers, feature-dev, pr-review-toolkit, security-guidance, commit-commands | `.ciclo-chatbot/estado.md` |
| 1 | Descoberta | `descoberta` | superpowers `brainstorming` | `docs/chatbot/01-descoberta.md` |
| 2 | Arquitetura e stack | `decidir-stack` | feature-dev `code-architect`, `c4-architecture`, Context7 | `docs/chatbot/02-arquitetura.md`, `docs/adr/` |
| 3 | Banco de dados | `modelar-banco` | `postgres-best-practices` (Supabase), `pg` (pg-aiguide), `database-architect` (wshobson) como segundo revisor, Squawk, Postgres MCP Pro | `docs/chatbot/03-banco.md`, schema e migrações |
| 4 | Camada de IA | `camada-ia` | `claude-api`, `llm-application-dev`, promptfoo | `docs/chatbot/04-ia.md`, `prompts/`, `evals/` |
| 5 | Providers WhatsApp | `providers-whatsapp` | design próprio; `twilio-developer-kit` ou MCP da 360dialog se aplicável | `docs/chatbot/05-whatsapp.md` |
| 6 | Implementação | `implementar` | superpowers (planos, TDD, subagentes), pr-review-toolkit | código em fatias verticais |
| 7 | Testes e evals | `testes-e-evals` | promptfoo, superpowers `verification-before-completion`, k6 | `docs/chatbot/07-qualidade.md` |
| 8 | Segurança | `auditoria-seguranca` | security-guidance, claude-security, Trail of Bits | `docs/chatbot/08-seguranca.md` |
| 9 | Publicação | `publicar` | railway / render / flyctl, cicd-automation, Sentry, Langfuse | `docs/chatbot/09-publicacao.md`, staging e produção no ar |
| 10 | Conexão WhatsApp | `conectar-whatsapp` | Claude in Chrome (opcional), MCP da 360dialog ou Twilio se aplicável | `docs/chatbot/10-go-live.md` |
| 11 | Operação | `operar` | Sentry, Langfuse, promptfoo | `docs/chatbot/11-runbook.md` |

Entradas, saídas e o checklist de saída de cada fase estão em `${CLAUDE_SKILL_DIR}/references/fases.md`. Ler o trecho da fase antes de começá-la e antes de apresentar o portão.

## Como executar uma fase

1. Marcar a fase como "em andamento" no estado.
2. Invocar a skill da fase com a ferramenta Skill (`ciclo-chatbot:<skill>`).
3. Ao terminar, rodar o checklist de saída da fase.
4. Apresentar o portão no formato abaixo e esperar.
5. Com aprovação: marcar a fase como concluída, registrar decisões e peças usadas no estado, e avançar.

## Formato do portão

```
Fase N (<nome>): pronta para aprovação
Feito: <3 a 5 linhas>
Decisões (com ADR ou fonte): <lista curta>
Riscos e pendências: <lista curta>
Próxima fase: <nome>. Vou precisar de você para: <credenciais, decisões>
Aprova?
```

Usar AskUserQuestion para a aprovação quando houver alternativas a escolher; caso contrário, uma pergunta direta.

## Fora de ordem e paralelismo

- O usuário pode pedir uma fase isolada ("revisa meu banco", "conecta no WhatsApp"). Chamar a skill da fase diretamente e registrar no estado. Se faltar um artefato de fase anterior, fazer só as perguntas mínimas daquela fase, sem rodá-la inteira.
- Depois do banco aprovado, as fases 4 e 5 podem ser desenhadas em paralelo pelos agentes `engenheiro-ia` e `especialista-whatsapp`, porque só dependem dos nomes das tabelas.
- A fase 6 começa por um esqueleto ponta a ponta (webhook → banco → resposta) para reduzir risco cedo; ver `ciclo-chatbot:implementar`.
