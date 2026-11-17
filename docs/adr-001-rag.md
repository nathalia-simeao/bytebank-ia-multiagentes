# ADR-001 — Preferir RAG a fine-tuning para consulta de políticas

**Status:** Aceito para protótipo | **Data:** 2026-11-17 | **Decisores fictícios:** PO, Tech Lead, Compliance, Segurança

## Contexto

Políticas de conta, cartão e segurança são documentais, sujeitas a mudanças e requerem procedência verificável. A solução deve permitir corrigir informações sem re-treinar modelo e não deve executar decisões financeiras autonomamente.

## Alternativas

1. **Somente prompt estático:** simples e barato, mas difícil manter conhecimento extenso e atualizado; baixo controle das fontes.
2. **Fine-tuning:** pode ajustar estilo e comportamento, mas exige curadoria de exemplos, custos de treino, revalidação e não garante conhecimento atualizado ou correto.
3. **RAG com recuperação:** atualiza documentos separadamente, usa metadados/ACL, permite citar trechos e auditar falhas. Acrescenta complexidade do retriever e dependência de recuperação correta.

## Decisão

Usar **RAG** como fonte primária de conhecimento, com processo editorial de atualização e avaliação de recuperação. Fine-tuning poderá ser estudado futuramente para **comportamento, linguagem e classificação**, mas não como substituição de documentos vigentes. O protótipo possui modo offline, vetorial opcional e escalonamento humano obrigatório em casos sensíveis.

## Escolha de vector store

| Opção | Benefícios | Custos/limites no cenário |
|---|---|---|
| ChromaDB | API Python simples, roda localmente, facilita protótipo | Persistência e governança empresarial precisam de desenho específico |
| FAISS | Busca vetorial local eficiente, biblioteca madura | Não fornece sozinho toda a camada de metadados, ACL e operação |
| Supabase/pgvector | Integra com PostgreSQL, SQL e controles de acesso | Infraestrutura, administração e custos de cloud para uma prova de conceito |

**Escolhida:** ChromaDB para prototipar; uma solução gerenciada ou PostgreSQL poderá ser reavaliada em produção conforme requisitos de segurança, volume e SLO.

## Embeddings e metadados

Embeddings permitem recuperar textos similares por significado. A base sintética pequena não prova qualidade semântica. Os metadados `dominio`, `secao` e `categoria` apoiam filtros/avaliações; `nivel_acesso` é critério de autorização e deve ser aplicado **antes** do retorno de documentos. A fonte `id` permite inspeção e rastreabilidade.

## Consequências e trade-offs

- **Vantagens:** atualização sem treino, transparência, economia de contexto, seleção contextual.
- **Desvantagens:** custo por embedding/consulta em provedores pagos; erros de chunking; recall imperfeito; latência de retrieval; necessidade de validação contínua.
- **Mitigações:** suite de 8 casos para começo, métricas separadas de qualidade, controle de acesso, fallback de insuficiência e aprovação humana.

