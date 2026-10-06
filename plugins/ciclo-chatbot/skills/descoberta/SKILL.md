---
name: descoberta
description: Conduz a descoberta de um chatbot com IA para WhatsApp e produz o briefing que alimenta todas as fases seguintes, incluindo intenções, escopo, volumes para dimensionar o banco, base de conhecimento, integrações, atendimento humano, templates e opt-in, LGPD, métricas, orçamento e conformidade com a política da Meta para bots de IA. Usar quando o usuário disser "tenho uma ideia de chatbot", "definir escopo do bot", "briefing do chatbot", "o que o bot vai fazer", ou na fase 1 do /ciclo-chatbot:iniciar.
argument-hint: "[descrição curta da ideia]"
---

# Descoberta

Objetivo: sair com `docs/chatbot/01-descoberta.md` preenchido a partir de `${CLAUDE_SKILL_DIR}/references/briefing-template.md`, com respostas do usuário, e não com suposições.

## Como conduzir

1. Se a skill `superpowers:brainstorming` estiver disponível, usar só o método dela para conduzir a conversa: uma pergunta por vez, alternativas quando houver, validação do entendimento por partes. Não deixar que ela grave o próprio documento de especificação nem que chame `writing-plans` ao final: o único artefato desta fase é `docs/chatbot/01-descoberta.md`, e a fase termina no portão. Se a skill não estiver disponível, seguir o mesmo método manualmente.
2. Começar pelo negócio e pelas intenções; deixar tecnologia para a fase 2.
3. Pedir exemplos reais de mensagens de clientes (prints, exportações de conversas, perguntas frequentes). Eles viram casos de eval na fase 4.
4. Quando o usuário não souber um número (volume, pico), registrar uma estimativa com faixa (mínimo, provável, máximo) e a origem dela.
5. Usar AskUserQuestion para escolhas fechadas (single ou multi-tenant, provedores, canais de atendimento humano).

## Tópicos obrigatórios

Seguir a ordem do template. Os pontos que mais mudam as fases seguintes:

- **Volumes** (definem particionamento, índices, filas e custo): contatos ativos por mês, mensagens por dia, pico por minuto, tamanho médio de conversa, crescimento em 12 e 24 meses.
- **Base de conhecimento**: tamanho aproximado em tokens. Abaixo de cerca de 200 mil tokens, a Anthropic recomenda considerar colocar a base inteira no prompt com cache, sem RAG ([Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)).
- **Ações do bot**: o que ele executa sozinho (consultar, agendar, cancelar, cobrar) e o que exige confirmação humana.
- **Mensagens proativas**: fora da janela de 24h após a última mensagem do cliente, só é possível enviar templates aprovados ([Meta: enviar mensagens](https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/send-messages)). Lembretes, follow-ups e retornos de atendimento humano tardios dependem de templates.
- **Opt-in**: a Meta exige opt-in que identifique a empresa e respeito ao opt-out ([Meta: opt-in](https://developers.facebook.com/documentation/business-messaging/whatsapp/getting-opt-in/)).
- **Multi-tenant**: se for um SaaS que conecta números de vários clientes, o onboarding passa pelo Embedded Signup (fase 10) e o banco precisa de isolamento por tenant.

## Conformidade com a política da Meta (checar sempre)

- Os [WhatsApp Business Solution Terms](https://www.whatsapp.com/legal/business-solution-terms) (vigentes desde 2026-03-06) proíbem provedores de IA quando a IA é a funcionalidade principal oferecida, com exceções para usuários do EEE e do Brasil; bots que atendem clientes de um negócio (suporte, agendamento, pedidos) seguem permitidos. Os mesmos termos proíbem usar dados da plataforma para criar, treinar ou melhorar sistemas de IA, com exceção de fine-tuning para uso interno exclusivo: registrar isso nas decisões de dados.
- No Brasil, o CADE impôs medida preventiva contra a regra e, em 2026-04-23, manteve multa diária de R$ 250 mil por descumprimento ([CADE](https://www.gov.br/cade/pt-br/assuntos/noticias/cade-mantem-multa-diaria-contra-meta-e-whatsapp-por-descumprimento-de-medida-preventiva)). A situação jurídica ainda muda; desenhar o bot com escopo de negócio de qualquer forma.
- Registrar no briefing a frase que descreve o bot como serviço de um negócio. Se a ideia for um assistente geral, apontar o risco ao usuário antes de seguir.

## Custos a estimar

- **Meta**: cobrança por mensagem desde 2025-07-01. A Meta anuncia que, a partir de 2026-10-01, mensagens de serviço (respostas dentro da janela de 24h) também são cobradas, com a mesma tarifa de utility do mercado ([Meta: preços de mensagens sem template](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing/non-template-messages)). Conferir a página e a fatura na data, porque o anúncio ainda aparecia como "upcoming". Isso favorece uma resposta consolidada em vez de várias bolhas.
- **LLM**: tokens por conversa vezes conversas por mês, por modelo. Preços atuais pela skill `claude-api` ou pela página de modelos do provider.
- **Infraestrutura**: estimativa inicial do PaaS (fase 2 detalha).

## Saída e portão

- Escrever `docs/chatbot/01-descoberta.md` com fontes e data das consultas.
- Rodar o checklist da fase 1 em `ciclo-chatbot:iniciar` (arquivo `references/fases.md` daquela skill) e apresentar o portão.
