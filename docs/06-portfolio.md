# Narrativa de portfólio — Bytebank AI

## Quem sou

Sou **Nathalia Simeão**, profissional de comunicação, marketing e tecnologia, com atuação em CRM, integrações, automação, dados e produtos digitais. Neste projeto, aprofundei competências de engenharia de sistemas de IA, combinando visão de produto e execução técnica.

## O problema

Uma empresa fictícia precisava responder dúvidas recorrentes sobre políticas bancárias, mas sem transformar um chatbot em uma fonte de informações inventadas ou em um aprovador autônomo de decisões sensíveis.

## Minha abordagem

Estruturei governança e funções do time, defini princípios éticos e práticas de LLMOps, modelei um RAG com fontes e controle de acesso, construí um protótipo executável com avaliação reproduzível e organizei três agentes especializados em um fluxo supervisionado. Documentei os papéis dos protocolos A2A e MCP e adicionei um ponto de decisão humana para solicitações Platinum simuladas.

## Evidências

- Dataset sintético com 50 documentos e metadados.
- Código Python testável sem gastos de API.
- Caminho opcional para embeddings + Chroma e LangGraph StateGraph.
- Diagramas exportados e documentação de decisões.
- Testes unitários e 8 casos de avaliação.
- README que explica execução, premissas e limitações.

## Principais desafios

1. **Confiabilidade:** responder apenas com evidências e informar quando uma resposta não está disponível.
2. **Privacidade:** aplicar filtragem de documentos por perfil antes de entregá-los ao modelo.
3. **Orquestração:** separar domínios e evitar que o agente de cartões aprove crédito sem intervenção humana.
4. **Métricas honestas:** não confundir recuperação de fontes ou presença de palavras com qualidade factual completa.

## Próximos passos

Avaliar o RAG vetorial com modelo configurado, implementar re-ranking com cross-encoder, validar rubricas humanas, testar ataques de prompt injection e simular um provedor de ferramentas MCP seguro — sempre em ambiente fictício.

---

### Texto sugerido para LinkedIn

> Concluí um projeto de portfólio voltado a sistemas de IA responsáveis: governança, pipeline RAG com fontes rastreáveis, avaliação, arquitetura multiagente e Human-in-the-Loop. O case simula o Bytebank e demonstra como combinar agentes especializados e recuperação documental sem abrir mão da transparência e da supervisão humana. Código, documentação, diagramas e testes estão disponíveis no meu GitHub. #InteligenciaArtificial #RAG #LangGraph #LLMOps #Multiagentes

