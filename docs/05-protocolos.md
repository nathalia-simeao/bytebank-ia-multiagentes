# Protocolos — A2A, MCP e decisões de segurança

## Diferenças e casos de uso

| Critério | A2A (entre agentes) | MCP (agente ↔ ferramentas/recursos) |
|---|---|---|
| Propósito | Delegação e coordenação entre especialistas | Exposição padronizada de capacidades externas |
| Unidade de interação | Tarefa, mensagem, status, artefato | Tool call, recurso, prompt |
| Caso Bytebank | Supervisor transfere consulta ao agente de cartões | Agente consulta um saldo ou uma fatura em sistema autorizado |
| Descoberta | Agent Card / capacidades de agente | Lista de ferramentas e schemas do servidor |
| Risco | Encaminhamento indevido ou perda de contexto | Execução de operações não autorizadas ou vazamento de dados |

**Por que combinar:** A2A coordena **quem** deve executar uma tarefa; MCP padroniza **como** cada agente acessa funções externas. Protocolos não substituem autenticação, autorização, auditoria e regras de negócio.

## Exemplos ilustrativos

### Agent Card (formato didático simplificado)

```json
{
  "name": "bytebank-cartoes",
  "description": "Especialista fictício em políticas de cartões e faturas",
  "version": "1.0.0",
  "skills": ["consultar_politica_cartao", "encaminhar_aprovacao_platinum"],
  "capabilities": {"streaming": false},
  "requires_authenticated_session": true
}
```

### Mensagem A2A (payload didático, não especificação literal)

```json
{
  "correlation_id": "demo-42",
  "from": "supervisor",
  "to": "bytebank-cartoes",
  "task": "consultar_politica_cartao",
  "input": {"question": "Quais são os requisitos para Platinum?"},
  "access_level": "publico",
  "expected_output": "resposta_com_fonte"
}
```

### Ferramenta MCP (schema ilustrativo)

```json
{
  "name": "consultar_fatura",
  "description": "Consulta fatura de titular autenticado em serviço autorizado",
  "inputSchema": {
    "type": "object",
    "properties": {"competencia": {"type": "string", "description": "Mês no formato AAAA-MM"}},
    "required": ["competencia"],
    "additionalProperties": false
  }
}
```

No mundo real, a identidade do titular deve vir do contexto seguro da sessão; o modelo não pode escolher IDs de outros clientes. Os exemplos acima são **esquemas explicativos** e não servidores conformes integralmente com as especificações A2A ou MCP.

## Decisões de arquitetura

- **Escopo de descoberta:** somente agentes e ferramentas explicitamente permitidos e versionados.
- **Escopo de autorização:** usuário, consentimento e política; identidades são propagadas com mínimo privilégio.
- **Segurança nas mutações:** confirmação antes da chamada, idempotência, limites, prova de autorização e trilha de auditoria.
- **Intervenção humana:** solicitação Platinum interrompe execução antes de qualquer ação; o revisor aprova ou recusa.
- **Confiabilidade:** timeouts, limite de tentativas, fallback e não repetição de operações financeiras.
- **Observabilidade:** correlação entre agente, ferramenta, fontes e decisão, com logs minimizados.

