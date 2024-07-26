import os
import base64
import requests
from dotenv import load_dotenv

from taipy.gui import Gui, notify
import taipy.gui.builder as tgb

from PIL import Image

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def on_init(state):
    state.conv.update_content(state, "")
    state.messages_dict = {}
    state.messages = [
        {
            "role": "assistant",
            "style": "assistant_message",
            "content": "Hi, I'm GPT-4o! How can I help you today?",
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
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }

    if state.query_image_path != "":
        base64_image = encode_image(state.query_image_path)
        message = {
            "role": "user",
            "content": [
                {"type": "text", "text": f"{state.query_message}"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        }
    else:
        message = {
            "role": "user",
            "content": [{"type": "text", "text": f"{state.query_message}"}],
        }

    state.gpt_messages.append(message)

    payload = {
        "model": "gpt-4o",
        "messages": state.gpt_messages,
        "max_tokens": 300,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )

    return (
        response.json()
        .get("choices")[0]
        .get("message")
        .get("content")
        .replace("\n\n", "\n")
    )


def send_message(state):
    if state.query_image_path == "":
        state.messages.append(
            {
                "role": "user",
                "style": "user_message",
                "content": state.query_message,
            }
        )
    else:
        state.messages.append(
            {
                "role": "user",
                "style": "user_message",
                "content": f"{state.query_message}\n![user_image]({state.query_image_path})",
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
    state.query_image_path = ""


def upload_image(state):
    try:
        global index
        image = Image.open(state.query_image_path)
        image.thumbnail((300, 300))
        image.save(f"images/example_{index}.png")
        state.query_image_path = f"images/example_{index}.png"
        index = index + 1
    except:
        notify(
            state,
            "error",
            f"Please make sure your image is under 1MB",
        )


def reset_chat(state):
    state.messages = []
    state.gpt_messages = []
    state.query_message = ""
    state.query_image_path = ""
    state.conv.update_content(state, create_conv(state))
    on_init(state)


if __name__ == "__main__":
    index = 0
    query_image_path = ""
    query_message = ""
    messages = []
    gpt_messages = []
    messages_dict = {}

    with tgb.Page() as page:
        with tgb.layout(columns="300px 1"):
            with tgb.part(class_name="sidebar"):
                tgb.text("## Taipy x GPT-4o", mode="md")
                tgb.button(
                    "New Conversation",
                    class_name="fullwidth plain",
                    id="reset_app_button",
                    on_action=reset_chat,
                )
                tgb.html("br")
                tgb.image(
                    content="{query_image_path}", width="250px", class_name="image_preview"
                )

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
                    tgb.file_selector(
                        content="{query_image_path}",
                        on_action=upload_image,
                        extensions=".jpg,.jpeg,.png",
                        label="Upload an image",
                    )
                    tgb.text("Max file size: 1MB")
    gui = Gui(page)
    conv = gui.add_partial("")
    gui.run(title="🤖Taipy x GPT-4o", dark_mode=False, margin="0px", debug=True)
