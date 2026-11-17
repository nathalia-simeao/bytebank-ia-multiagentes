# Etapa 3 — Pipeline funcional e avaliação

## Componentes executáveis

- [`policies.py`](../src/bytebank/policies.py): leitura de CSV, validação, limpeza de texto, categorias e chunks com metadados.
- [`rag.py`](../src/bytebank/rag.py): busca de 8 candidatos, re-ranking lexical dos 4 melhores, geração com contexto e IDs citados.
- [`agents.py`](../src/bytebank/agents.py): supervisor e especialistas, suporte a LangGraph opcional.
- [`scripts/run_demo.py`](../scripts/run_demo.py): CLI de consulta.
- [`scripts/evaluate.py`](../scripts/evaluate.py): avaliação sobre [8 casos](../data/validacao.csv).

## Execução

```bash
python scripts/run_demo.py --pergunta "Como abrir uma conta corrente?"
python scripts/evaluate.py
python -m unittest discover -s tests -v
```

Com API configurada e extras instalados:

```bash
python scripts/run_demo.py --pergunta "Quais são os requisitos Platinum?" --vetorial --llm
python scripts/evaluate.py --with-llm
```

## Resultados e interpretação

O arquivo [results/avaliacao.md](../results/avaliacao.md) contém a execução local reproduzível. As métricas são:

- **Hit@4 documental:** proporção de perguntas em que o ID esperado está entre as 4 fontes finais.
- **Cobertura de termos:** proporção de termos-alvo presentes na resposta extrativa. É um **proxy**, sensível a paráfrases e sujeito a falsos positivos.
- **Taxa de abstenção:** quantas perguntas sem fonte resultam em resposta de insuficiência, verificável nos testes.

**Não equiparar Hit@4 ou correspondência de termos à precisão factual da IA.** A revisão deve verificar fidelidade, completude, segurança, citações, confidencialidade e possíveis omissões. O modo sem API usa busca lexical, não um LLM gerador.

## Protocolo para comparação LLM sem RAG × com RAG

1. Fixar versão do modelo, temperatura, dataset, acesso, idioma e prompts. Não permitir que o modelo sem RAG veja as respostas esperadas.
2. Executar **sem RAG**: o mesmo LLM responde às 8 perguntas sem contexto recuperado.
3. Executar **com RAG**: LLM recebe os quatro trechos com fonte. Registrar IDs e respostas.
4. Fazer avaliação cega por humano com rubrica de 0–2 para **correção**, **fundamentação**, **completude** e **segurança**. Um segundo avaliador resolve divergências.
5. Calcular `acurácia = respostas com correção 2 / total`, acompanhada de taxa de abstenção, custo estimado, latência e violações de acesso.
6. Registrar data, versão do modelo, prompts e dataset. **Não publicar números de comparação que não tenham sido realmente medidos.**

## Testes de segurança mínimos

- Perfil `publico` não recupera políticas `interno` ou `restrito`.
- Perguntas totalmente não relacionadas geram abstenção.
- Uma solicitação Platinum é classificada como cartão e fica **pendente de decisão humana**, nunca sendo aprovada pelo modelo.
- A decisão humana é simulada e registrada apenas em memória; não chama API bancária.

## Próxima iteração

Adicionar testes de recuperação por significado (sinônimos), cross-encoder como re-ranker, dados de vigência, filtros por domínio, automação de revisão de documentação e painel de métricas em ambiente seguro. Definir avaliações de qualidade com pessoas de compliance antes de qualquer uso real.

