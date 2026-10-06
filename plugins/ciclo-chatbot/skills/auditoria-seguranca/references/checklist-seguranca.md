# Checklist de segurança e conformidade

## Webhook
- [ ] Assinatura validada sobre o corpo bruto, antes de qualquer parse, com comparação em tempo constante (`crypto.timingSafeEqual`, `hmac.compare_digest`) ([Meta: webhooks](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/create-webhook-endpoint)).
- [ ] `hub.verify_token` aleatório e diferente por ambiente.
- [ ] Requisição sem assinatura ou com assinatura inválida: 401, sem gravar nada, log sem o corpo.
- [ ] Idempotência no banco; reenvios da Meta por até 7 dias não geram ação duplicada.
- [ ] Limite de tamanho do corpo coerente com o máximo da Meta (3 MB).
- [ ] Só HTTPS com certificado válido.

## Segredos
- [ ] Token de acesso, app secret, chaves de LLM e de banco só no cofre de segredos do PaaS, por ambiente ([12factor III](https://12factor.net/config)).
- [ ] Nenhum segredo no repositório, em imagem Docker, em argumento de build, em log ou em trace.
- [ ] Token de usuário do sistema com as permissões mínimas e plano de rotação.

## Banco
- [ ] Aplicação conecta com papel que não é superusuário, não tem `BYPASSRLS` e não é dono das tabelas ([PG: RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)).
- [ ] RLS habilitado e forçado nas tabelas de negócio (multi-tenant) e testado: sem tenant definido, zero linhas.
- [ ] Migrações com papel separado.
- [ ] Postgres MCP e similares nunca apontados para produção com escrita.

## LLM e ferramentas
- [ ] Mitigações do OWASP LLM Top 10 (2025) da fase 4 implementadas e testadas no red team ([OWASP](https://genai.owasp.org/llm-top-10/)).
- [ ] Ferramentas validam parâmetros no código e checam permissão do contato (um contato não age sobre dados de outro).
- [ ] Ações com consequência exigem confirmação.
- [ ] Limite de mensagens e tokens por contato e teto de custo por tenant (LLM10).
- [ ] System prompt sem segredos (LLM07).
- [ ] Para agentes com ferramentas: itens do OWASP Agentic Top 10 (2026) revisados ([OWASP](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)).

## Dados pessoais e LGPD
- [ ] Telefone em hash e conteúdo sensível mascarado em logs e traces (Langfuse, Sentry).
- [ ] Retenção por tabela implementada como job e testada.
- [ ] Fluxo de pedido do titular (acesso, correção, anonimização, eliminação) implementado e testado de ponta a ponta, incluindo embeddings e payloads brutos (arts. 18 e 16).
- [ ] Caminho de revisão humana para decisões automatizadas (art. 20).
- [ ] Transferência internacional para APIs de LLM documentada (art. 33).
- [ ] Plano de resposta a incidentes com comunicação à ANPD e aos titulares quando aplicável (art. 48).
- Fonte: [Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm).

## WhatsApp
- [ ] Opt-in registrado antes de mensagens proativas; opt-out respeitado imediatamente ([Meta: opt-in](https://developers.facebook.com/documentation/business-messaging/whatsapp/getting-opt-in/)).
- [ ] Nenhum adapter `official: false` em produção sem ADR.
- [ ] Bot descrito como serviço do negócio (política de bots de IA, ver `providers-whatsapp/references/cloud-api.md`).

## Infraestrutura
- [ ] Imagem com usuário não root, base mínima e versão fixada ([Docker: best practices](https://docs.docker.com/build/building/best-practices/)).
- [ ] Dependências fixadas (lockfile) e auditadas no CI.
- [ ] Rotas internas e painéis protegidos; health check não expõe detalhes internos.
