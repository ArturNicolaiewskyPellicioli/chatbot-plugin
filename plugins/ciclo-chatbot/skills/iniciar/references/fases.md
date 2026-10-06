# Fases: entradas, saídas e checklist de saída

Cada checklist é o critério do portão. Item não cumprido vira pendência explícita no portão, com o motivo, ou bloqueia a fase.

## 0. Ambiente
- Entrada: repositório do projeto (vazio ou existente).
- Saída: núcleo da comunidade instalado; `.ciclo-chatbot/estado.md` criado.
- Checklist:
  - [ ] superpowers, feature-dev, pr-review-toolkit, security-guidance e commit-commands instalados, ou ausência registrada com o fallback escolhido
  - [ ] MCP Context7 respondendo
  - [ ] Git inicializado e branch principal protegida (ou combinado com o usuário)

## 1. Descoberta
- Entrada: ideia do usuário.
- Saída: `docs/chatbot/01-descoberta.md`.
- Checklist:
  - [ ] Objetivo de negócio e 3 a 7 intenções principais, com exemplos reais de mensagens
  - [ ] Fora de escopo escrito (o que o bot recusa ou passa para humano)
  - [ ] Bot atende clientes de um negócio, e não é um assistente de IA de uso geral (política da Meta; ver `ciclo-chatbot:descoberta`)
  - [ ] Volumes estimados: contatos por mês, mensagens por dia, pico por minuto, crescimento em 12 a 24 meses
  - [ ] Base de conhecimento: fontes, tamanho aproximado em tokens, frequência de atualização
  - [ ] Integrações de negócio (agenda, CRM, ERP, pagamentos) e quais ações o bot pode executar sozinho
  - [ ] Atendimento humano: quem, horário, ferramenta
  - [ ] Mensagens proativas (templates) e coleta de opt-in
  - [ ] LGPD: dados pessoais tratados, base legal, retenção, direitos do titular
  - [ ] Métricas de sucesso e orçamento mensal (LLM + Meta por mensagem + infraestrutura)
  - [ ] Single-tenant ou multi-tenant (SaaS com vários clientes e números)

## 2. Arquitetura e stack
- Entrada: descoberta aprovada.
- Saída: `docs/chatbot/02-arquitetura.md`, ADRs em `docs/adr/`.
- Checklist:
  - [ ] Matriz de decisão preenchida com pesos e notas justificadas
  - [ ] ADRs aceitos: linguagem e framework, ORM e migrações, fila, provider e framework de LLM, PaaS e região, estrutura modular, observabilidade, providers de WhatsApp
  - [ ] Diagrama C4 de contexto e de containers (web, worker, Postgres, Redis, providers, LLM)
  - [ ] Versões conferidas na documentação oficial (Context7), com data

## 3. Banco de dados
- Entrada: descoberta e ADRs.
- Saída: `docs/chatbot/03-banco.md`, schema no ORM escolhido, migrações SQL.
- Checklist:
  - [ ] ERD e dicionário de dados
  - [ ] Cada índice ligado à consulta que atende; nenhuma FK sem índice
  - [ ] Idempotência de webhook garantida por constraint única
  - [ ] Isolamento por tenant definido (RLS ou equivalente) se multi-tenant
  - [ ] Estratégia de particionamento e retenção decidida com base no volume projetado
  - [ ] pgvector: tipo, dimensão, índice e estratégia de filtro decididos
  - [ ] Migrações aplicadas num Postgres real e sem alertas do Squawk (em Alembic ou TypeORM, no SQL gerado)
  - [ ] Consultas críticas testadas com `EXPLAIN (ANALYZE, BUFFERS)` em volume sintético
  - [ ] Revisão do agente `revisor-banco` sem bloqueios abertos
  - [ ] Plano de LGPD: anonimização, exclusão em cascata, retenção por tabela

## 4. Camada de IA
- Entrada: descoberta, ADRs, modelo de dados.
- Saída: `docs/chatbot/04-ia.md`, `prompts/`, `evals/` com o conjunto inicial.
- Checklist:
  - [ ] Pipeline por mensagem desenhado (guarda, roteador, handlers, checagem de saída)
  - [ ] Modelos por papel, com preços conferidos na data
  - [ ] Estratégia de cache de prompt e de memória (janela, resumo, fatos do contato)
  - [ ] RAG: estratégia decidida (contexto inteiro com cache ou recuperação híbrida com rerank)
  - [ ] Ferramentas com privilégio mínimo e aprovação humana para ações com consequência
  - [ ] Mapeamento OWASP LLM Top 10 (2025) e gatilhos de transbordo para humano
  - [ ] 20 a 50 casos de eval com critérios de aprovação, incluindo casos adversariais

## 5. Providers WhatsApp
- Entrada: ADRs e modelo de dados.
- Saída: `docs/chatbot/05-whatsapp.md`.
- Checklist:
  - [ ] Porta (interface) e eventos normalizados definidos
  - [ ] Adapters escolhidos e flag `official` correta em cada um
  - [ ] Pipeline de webhook: corpo bruto, assinatura pelo app do provider, conta resolvida e conferida por evento, gravação idempotente, fila, 200 rápido
  - [ ] Processamento serializado por conversa, com debounce de rajadas
  - [ ] Janela de 24h, limites de vazão (por número e por destinatário) e retentativas definidos
  - [ ] Identidade do usuário com BSUID e telefone (telefone pode não vir no webhook)
  - [ ] Roteamento por número e política de dois providers simultâneos

## 6. Implementação
- Entrada: fases 2 a 5 aprovadas.
- Saída: código das fatias, testes verdes.
- Checklist por fatia:
  - [ ] Plano escrito antes do código
  - [ ] Testes escritos antes da implementação
  - [ ] Revisão de modularidade sem duplicação relevante e sem violação de fronteira entre módulos
  - [ ] Revisão de código sem achados de alta confiança abertos
  - [ ] Verificação com evidência (comandos rodados e saída) antes de declarar pronto

## 7. Testes e evals
- Checklist:
  - [ ] Testes unitários, de integração (Postgres real) e de contrato por provider passando
  - [ ] Evals acima da meta definida na descoberta; red team sem falhas críticas
  - [ ] Teste de carga: webhook responde dentro do orçamento no pico projetado; fila não acumula

## 8. Segurança
- Checklist:
  - [ ] Nenhum achado alto ou crítico aberto
  - [ ] Assinatura de webhook validada no corpo bruto, com comparação em tempo constante
  - [ ] Segredos fora do código, do banco e dos logs
  - [ ] Telefone e conteúdo pessoal fora de traces e logs (hash ou mascaramento)
  - [ ] Checklist LGPD atendido

## 9. Publicação
- Checklist:
  - [ ] Staging e produção separados, com segredos por ambiente
  - [ ] CI com lint, tipos, testes, Squawk e evals antes do deploy
  - [ ] Migrações no comando de pré-deploy da plataforma, nunca no boot
  - [ ] Health checks verdes; worker com desligamento gracioso
  - [ ] Backups e PITR ativos; restauração testada
  - [ ] Rollback ensaiado

## 10. Conexão WhatsApp
- Checklist:
  - [ ] Checklist de go-live da Meta completo
  - [ ] Mensagem real enviada de um celular, respondida em produção, com status `delivered` e `read` gravados
  - [ ] Templates necessários aprovados

## 11. Operação
- Checklist contínuo: painéis e alertas ativos, ciclo semanal de evals com tráfego real, revisão mensal de custos e versões.
