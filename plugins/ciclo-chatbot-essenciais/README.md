# ciclo-chatbot-essenciais

Pacote opcional. Instala de uma vez, como dependências, as cinco peças núcleo da comunidade que o `ciclo-chatbot` usa em todas as fases, todas do marketplace oficial da Anthropic (`claude-plugins-official`, que já vem configurado no Claude Code):

- `superpowers`: brainstorming, planos, TDD, desenvolvimento por subagentes, depuração sistemática, verificação antes de concluir
- `feature-dev`: exploração e arquitetura de funcionalidades
- `pr-review-toolkit`: revisão de código com agentes especializados
- `security-guidance`: verificações de segurança sempre ativas em edições e commits
- `commit-commands`: commits e PRs

```
/plugin install ciclo-chatbot-essenciais@ciclo-chatbot-marketplace
```

As demais peças (banco, IA, deploy etc.) dependem da stack e do PaaS de cada projeto e são instaladas pela skill `/ciclo-chatbot:preparar-ambiente`.
