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
git clone https://github.com/Avaiga/demo-gpt-4o.git
```

2. Switch to the rag branch:

```bash
git checkout rag
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. `libmagic` returns an error with these dependencies. To fix it, run the following commands:

```bash
pip uninstall python-magic
pip install python-magic-bin==0.4.14
```

5. Install poppler:

For Windows (look online for other OS):
- Download the latest version of poppler from [here](https://github.com/oschwartz10612/poppler-windows/releases/).
- Unzip it and add the bin folder to your PATH.

6. Install tesseract:

For Windows (look online for other OS):
- Download the latest version of tesseract from [here](https://github.com/UB-Mannheim/tesseract/wiki).
- Install it and add the `C:\Program Files\Tesseract-OCR` folder to your PATH.

7. Create a `.env` file in the root directory with the following content:

```bash
HUGGINGFACEHUB_API_TOKEN=[YOUR_ACCESS_TOKEN]
```

8. Add your pdf files to the `pdfs` directory.

9. Run the app and ask questions about the content of the pdfs:

```bash
python main.py
```