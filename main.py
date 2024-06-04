import os
import base64
from dotenv import load_dotenv

from taipy.gui import Gui, notify
import taipy.gui.builder as tgb

import pandas as pd

from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFaceEndpoint
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA

load_dotenv()

os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")

PDF_FOLDER_PATH = "./pdfs"
pdf_names = os.listdir(PDF_FOLDER_PATH)
pdf_names = pd.DataFrame(pdf_names, columns=["Uploaded PDFs"])

loaders = [
    UnstructuredPDFLoader(os.path.join(PDF_FOLDER_PATH, fn))
    for fn in os.listdir(PDF_FOLDER_PATH)
]

index = VectorstoreIndexCreator(
    embedding=HuggingFaceEmbeddings(),
    text_splitter=CharacterTextSplitter(chunk_size=1000, chunk_overlap=0),
).from_loaders(loaders)

llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2", temperature=0.1, max_length=512
)


chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=index.vectorstore.as_retriever(),
    input_key="question",
)

index = 0
query_message = ""
messages = []
gpt_messages = []
messages_dict = {}


def on_init(state):
    state.conv.update_content(state, "")
    state.messages_dict = {}
    state.messages = [
        {
            "role": "assistant",
            "style": "assistant_message",
            "content": "Hi, I am your RAG assistant! How can I help you today?",
        },
    ]
    state.gpt_messages = []
    new_conv = create_conv(state)
    state.conv.update_content(state, new_conv)


def create_conv(state):
    messages_dict = {}
    with tgb.Page() as conversation:
        for i, message in enumerate(state.messages):
            text = message["content"].replace("<br>", "\n").replace('"', "'")
            messages_dict[f"message_{i}"] = text
            tgb.text(
                "{messages_dict['" + f"message_{i}" + "'] if messages_dict else ''}",
                class_name=f"message_base {message['style']}",
                mode="md",
            )
    state.messages_dict = messages_dict
    return conversation


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def query_gpt4o(state):
    message = {
        "role": "user",
        "content": [{"type": "text", "text": f"{state.query_message}"}],
    }

    state.gpt_messages.append(message)

    return chain.run(state.query_message)


def send_message(state):

    state.messages.append(
        {
            "role": "user",
            "style": "user_message",
            "content": state.query_message,
        }
    )

    state.conv.update_content(state, create_conv(state))
    notify(state, "info", "Sending message...")
    state.messages.append(
        {
            "role": "assistant",
            "style": "assistant_message",
            "content": query_gpt4o(state),
        }
    )
    state.conv.update_content(state, create_conv(state))
    state.query_message = ""


def reset_chat(state):
    state.messages = []
    state.gpt_messages = []
    state.query_message = ""
    state.conv.update_content(state, create_conv(state))
    on_init(state)


with tgb.Page() as page:
    with tgb.layout(columns="350px 1"):
        with tgb.part(class_name="sidebar"):
            tgb.text("## Taipy RAG", mode="md")
            tgb.button(
                "New Conversation",
                class_name="fullwidth plain",
                id="reset_app_button",
                on_action=reset_chat,
            )
            tgb.table("{pdf_names}", show_all=True)

        with tgb.part(class_name="p1"):
            tgb.part(partial="{conv}", height="600px", class_name="card card_chat")
            with tgb.part("card mt1"):
                tgb.input(
                    "{query_message}",
                    on_action=send_message,
                    change_delay=-1,
                    label="Write your message:",
                    class_name="fullwidth",
                )

if __name__ == "__main__":
    gui = Gui(page)
    conv = gui.add_partial("")
    gui.run(title="Taipy RAG", dark_mode=False, margin="0px", debug=True)
