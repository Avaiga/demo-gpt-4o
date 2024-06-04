# Taipy RAG Chatbot

<p align="center">
  <img src="media/rag_screenshot.png" alt="App Screenshot" width="100%"/>
</p>

A simple RAG chatbot that allows you to upload PDFs and query the model about the content.

This particular app uses Langchain, Huggingface and Mistral but it can be easily modified to use other models.

## How to Use

**You need a HuggingFace account with an active <a href="https://huggingface.co/settings/tokens" target="_blank">API key</a>**

1. Clone this repo:

```bash	

```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install poppler:

4. Install tesseract:

5. Create a `.env` file in the root directory with the following content:

```bash
HUGGINGFACEHUB_API_TOKEN=[YOUR_ACCESS_TOKEN]
```

6. Add your pdf files to the `pdfs` directory.

7. Run the app and ask questions about the content of the pdfs:

```bash
python main.py
```