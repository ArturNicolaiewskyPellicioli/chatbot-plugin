---
name: auditoria-seguranca
description: Audita a segurança e a conformidade de um chatbot de WhatsApp com IA antes do deploy, combinando o security-guidance sempre ativo, a varredura do claude-security, skills da Trail of Bits (insecure-defaults, supply-chain-risk-auditor, sharp-edges) e um auditor adversarial deste plugin com checklist de webhook, segredos, banco, OWASP LLM e Agentic e LGPD. Usar quando o usuário disser "auditar segurança", "revisão de segurança", "está seguro para produção?", "LGPD do bot", "prompt injection", ou na fase 8 do /ciclo-chatbot:iniciar.
argument-hint: "[completa | diff]"
---

# Auditoria de segurança

Saída: `docs/chatbot/08-seguranca.md` com achados por severidade (crítica, alta, média, baixa), evidência, correção e status. Checklist em `${CLAUDE_SKILL_DIR}/references/checklist-seguranca.md`.

## Passos

1. Confirmar que o plugin `security-guidance` está ativo (ele roda em edições e commits durante todo o ciclo).
2. Varreduras automáticas, em paralelo quando possível:
   - `/claude-security` (plugin `claude-security`) no repositório inteiro (modo `completa`) ou no diff da release (modo `diff`).
   - Skills da Trail of Bits, se instaladas: `insecure-defaults` (configurações padrão inseguras), `supply-chain-risk-auditor` (dependências), `sharp-edges` (APIs perigosas).
   - Auditoria de dependências do gerenciador de pacotes (`npm audit`, `pip-audit`).
3. Disparar o agente `auditor-seguranca` deste plugin com o checklist, os documentos das fases 3 a 5 e os relatórios das varreduras. Ele confirma ou descarta cada achado com evidência no código e procura o que as ferramentas não pegam (lógica do webhook, RLS, ferramentas do LLM, LGPD).
4. Consolidar sem duplicar: um achado por problema, com as ferramentas que o apontaram.
5. Corrigir críticos e altos com o ciclo da fase 6 (teste que reproduz → correção → verificação). Médios e baixos: corrigir ou aceitar com justificativa e prazo.
6. Rodar o checklist da fase 8 e apresentar o portão. Nenhum achado crítico ou alto pode ficar aberto.
