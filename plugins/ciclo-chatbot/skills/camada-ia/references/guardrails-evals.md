# Guardrails, transbordo e evals

## OWASP Top 10 para aplicações com LLM (2025)

Fonte: [genai.owasp.org/llm-top-10](https://genai.owasp.org/llm-top-10/). Para cada item, registrar em `04-ia.md` a mitigação concreta.

| Item | Mitigação típica neste bot |
|---|---|
| LLM01 Prompt Injection | conteúdo do contato e resultados de ferramentas sempre como dado (mensagem do usuário ou `tool_result`), nunca no system prompt; guarda de entrada; ferramentas com privilégio mínimo |
| LLM02 Sensitive Information Disclosure | nunca colocar dados de outros contatos no contexto; filtro de saída; RLS por tenant |
| LLM03 Supply Chain | dependências fixadas e auditadas; modelos e SDKs oficiais |
| LLM04 Data and Model Poisoning | ingestão da base só de fontes aprovadas; revisão de documentos novos |
| LLM05 Improper Output Handling | saída validada antes de virar ação ou mensagem; nunca executar texto do modelo |
| LLM06 Excessive Agency | ferramentas por intenção; aprovação humana para ações com consequência |
| LLM07 System Prompt Leakage | nada secreto no system prompt (chaves, regras de preço internas) |
| LLM08 Vector and Embedding Weaknesses | filtro por tenant em toda busca; chunks de fontes confiáveis |
| LLM09 Misinformation | resposta ancorada na base com citação; "não sei" + transbordo quando não houver fonte |
| LLM10 Unbounded Consumption | limite de mensagens e tokens por contato e por janela; teto de custo por tenant |

Para bots que usam ferramentas, cobrir também o OWASP Top 10 for Agentic Applications (2026), que trata de sequestro de objetivo, envenenamento de memória e contexto, entre outros ([OWASP](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)).

## Práticas da Anthropic contra jailbreak e injeção

Triagem de entrada com modelo pequeno e saída estruturada, conteúdo não confiável isolado, monitoramento de saídas, limitação de quem insiste em abusar ([mitigate jailbreaks](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks)). O OWASP lembra que um LLM usado como guarda também é suscetível a injeção: guarda não substitui privilégio mínimo ([cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)).

## Dados pessoais

- Presidio detecta PII, mas não tem garantia de detecção e precisa de reconhecedores próprios para documentos brasileiros como CPF ([Presidio](https://presidio.dataprivacystack.org/)). Usar como camada extra, não como única defesa.
- Em traces e logs, telefone vira hash e conteúdo sensível é mascarado.

## LGPD aplicada ao bot

Fonte: [Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm).
- Art. 6º: finalidade, necessidade (minimização), transparência.
- Art. 18: direitos do titular (acesso, correção, anonimização, bloqueio, eliminação).
- Art. 20: direito de pedir revisão de decisões tomadas só por tratamento automatizado. O transbordo para humano atende a isso; documentar o caminho.
- Art. 33: transferência internacional (APIs de LLM fora do Brasil): registrar a hipótese aplicável.
- Arts. 46 e 48: segurança e comunicação de incidentes.

## Gatilhos de transbordo para humano

Pedido explícito; duas falhas seguidas de entendimento; intenção de alto risco (reclamação formal, cancelamento com multa, assunto jurídico ou de saúde); fora de escopo recorrente; sentimento muito negativo. Fora da janela de 24h, o retorno do humano precisa de template aprovado.

## Evals

Método (fontes: [Anthropic: develop tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests), [Anthropic: evals for agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)):
- Muitos casos automatizados valem mais que poucos avaliados à mão. Preferência de avaliação: código, depois LLM com rubrica, depois humano.
- Rubricas com saída discreta (passa/falha ou escala curta) e raciocínio antes da nota.
- Começar com 20 a 50 casos tirados de falhas e conversas reais; separar suíte de capacidade (o que ainda não funciona) de suíte de regressão (o que não pode quebrar).
- Para consistência, rodar cada caso k vezes e exigir que passe em todas (pass^k) nos casos críticos.
- Conversas de vários turnos: usuário simulado por LLM.
- Ler as transcrições, não só as notas.

Ferramentas:
- promptfoo: asserções determinísticas, `llm-rubric` com `threshold`, red team, action de CI `promptfoo/promptfoo-action` ([CI](https://www.promptfoo.dev/docs/integrations/ci-cd/), [llm-rubric](https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/llm-rubric/)).
- Langfuse: datasets, experimentos e LLM-as-a-judge em traces de produção ([evaluation](https://langfuse.com/docs/evaluation/overview)).
