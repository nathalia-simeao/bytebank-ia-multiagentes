"""Interface Gradio opcional com aprovação humana explícita."""

from __future__ import annotations

from uuid import uuid4


def main() -> None:
    import gradio as gr
    from langgraph.types import Command

    from .agents import build_langgraph

    graph = build_langgraph()

    def reply(question: str, thread_id: str):
        config = {"configurable": {"thread_id": thread_id}}
        state = graph.invoke({"question": question, "access": "publico"}, config=config)
        if state.get("__interrupt__"):
            return "⏸️ Revisão humana necessária para a solicitação Platinum. Escolha aprovar ou recusar abaixo. Nenhuma ação bancária foi executada.", str(state.get("intent", "cartao_credito"))
        return state.get("answer", "Sem resposta"), state.get("intent", "suporte")

    def decide(approved: bool, thread_id: str):
        config = {"configurable": {"thread_id": thread_id}}
        if not graph.get_state(config).next:
            return "Não há decisão pendente nesta sessão."
        state = graph.invoke(Command(resume={"approved": approved}), config=config)
        return state.get("answer", "Decisão recebida")

    with gr.Blocks(title="Bytebank • IA responsável", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Bytebank • Assistente de IA\n**Protótipo educacional fictício.** Não insira dados pessoais ou bancários reais.")
        thread_id = gr.State(lambda: str(uuid4()))
        question = gr.Textbox(label="Sua pergunta", placeholder="Como solicitar cartão Platinum?", lines=2)
        submit = gr.Button("Consultar políticas")
        answer = gr.Textbox(label="Resposta e fontes", lines=12)
        intent = gr.Textbox(label="Agente selecionado", interactive=False)
        with gr.Row():
            approve = gr.Button("Aprovar simulação", variant="secondary")
            reject = gr.Button("Recusar simulação", variant="secondary")
        submit.click(reply, [question, thread_id], [answer, intent])
        approve.click(lambda t: decide(True, t), [thread_id], [answer])
        reject.click(lambda t: decide(False, t), [thread_id], [answer])
    demo.launch()


if __name__ == "__main__":
    main()

