import os
import sys
import time

sys.path.append("./")

from transformers import AutoModel, AutoTokenizer
import gradio as gr
from kbase import get_all_kbase, TextKnowledgeBase
from utils import jieba_ner

model_directory = "models/chatglm-6b-int4"
model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), model_directory)

tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
model = model.eval()

global_state_is_beginning = True
global_text_area_update = None
k_base_dic = {}

"""Override Chatbot.postprocess"""

from logics import postprocess, parse_text, process_file_upload, update_kbase_checkbox, \
    delete_kbase

gr.Chatbot.postprocess = postprocess


def update_system_msgbox():
    global global_state_is_beginning, global_text_area_update
    while global_state_is_beginning:
        time.sleep(0.2)
    return global_text_area_update


def load_kbase(k_bases):
    for k_base in k_bases:
        if k_base not in k_base_dic:
            k_base_dic[k_base] = TextKnowledgeBase(k_base)


def get_system_message(inp, k_bases):
    load_kbase(k_bases)
    prompt = "先验知识："
    recall_pairs = []
    for k_base in k_bases:
        title, content = k_base_dic[k_base].search(jieba_ner(inp))
        if title is None or content is None:
            continue
        recall_pairs.append((k_base, title, content))
        prompt += f"知识库：{k_base}, 内容：{content}; "
    prompt += "接下来请根据这些知识回答问题"

    return prompt, recall_pairs


def predict(input, k_bases, chatbot, max_length, top_p, temperature, history):
    global global_state_is_beginning, global_text_area_update
    if global_state_is_beginning:
        system_message, pairs = get_system_message(input, k_bases)

        recall_docs = ""
        if len(k_bases) == 0:
            recall_docs += "本次会话您未选取知识库"
        elif len(pairs) == 0:
            recall_docs += "很遗憾，知识库未找到相关内容"
        else:
            for idx, pair in enumerate(pairs):
                recall_docs += f"{pair[0]} 召回:\n标题: {pair[1]}\n内容:{pair[2]}\n\n"
            history.insert(0, (system_message, "好的"))

        global_text_area_update = gr.update(value=recall_docs)

    global_state_is_beginning = False
    chatbot.append((parse_text(input), ""))
    for response, history in model.stream_chat(tokenizer, input, history, max_length=max_length, top_p=top_p,
                                               temperature=temperature):
        chatbot[-1] = (parse_text(input), parse_text(response))

        yield chatbot, history


def reset_user_input():
    return gr.update(value='')


def reset_state():
    global global_state_is_beginning
    global_state_is_beginning = True
    return [], []


with gr.Blocks() as demo:
    gr.HTML("""<h1 align="center">ChatGLM</h1>""")

    with gr.Tab("Chat"):
        chatbot = gr.Chatbot()
        with gr.Row():
            with gr.Column(scale=3):
                with gr.Column(scale=12):
                    user_input = gr.Textbox(show_label=False, placeholder="Input...", lines=10).style(
                        container=False)
                with gr.Column(min_width=32, scale=1):
                    submitBtn = gr.Button("Submit", variant="primary")
            with gr.Column(scale=1):
                emptyBtn = gr.Button("清空对话")
                using_kbases = gr.CheckboxGroup(choices=get_all_kbase())
                max_length = gr.Slider(0, 4096, value=2048, step=1.0, label="Maximum length", interactive=True)
                top_p = gr.Slider(0, 1, value=0.7, step=0.01, label="Top P", interactive=True)
                temperature = gr.Slider(0, 1, value=0.95, step=0.01, label="Temperature", interactive=True)
            with gr.Column(scale=1):
                system_msg = gr.TextArea(label="知识库召回内容")

    with gr.Tab("Knowledge"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""<h1 align="center">知识库管理</h1>""")
                with gr.Row():
                    kbase_list = gr.CheckboxGroup(choices=get_all_kbase(), label="知识库列表", interactive=True)
                with gr.Row():
                    kbase_delete_btn = gr.Button("删除知识库")

            with gr.Column(scale=3):
                gr.HTML("""<h1 align="center">新增知识库</h1>""")
                kbase_name = gr.Textbox(placeholder="请输入你的知识库名字", label="知识库名字")
                knowledge_files = gr.File(file_count="directory")

                kbase_add_btn = gr.Button("新增知识库")

    history = gr.State([])

    submitBtn.click(predict,
                    inputs=[user_input, using_kbases, chatbot, max_length, top_p, temperature, history],
                    outputs=[chatbot, history],
                    show_progress=True)
    submitBtn.click(reset_user_input, [], [user_input])
    submitBtn.click(update_system_msgbox, outputs=[system_msg], show_progress=False)

    emptyBtn.click(reset_state, outputs=[chatbot, history], show_progress=True)

    kbase_add_btn.click(process_file_upload, inputs=[kbase_name, knowledge_files], show_progress=True)
    kbase_add_btn.click(update_kbase_checkbox, outputs=[kbase_list, using_kbases], show_progress=True)

    kbase_delete_btn.click(delete_kbase, inputs=[kbase_list], outputs=[kbase_list, using_kbases], show_progress=True)
    kbase_delete_btn.click(update_kbase_checkbox, outputs=[kbase_list, using_kbases], show_progress=True)

demo.queue().launch(inbrowser=True)
