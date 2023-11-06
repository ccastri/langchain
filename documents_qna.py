from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
import chainlit as cl
from chainlit.types import AskFileResponse
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
embeddings = OpenAIEmbeddings()

welcome_message = """Bienvenidos al servicio al cliente de CYC Accion Legal SAS:
1. Cargue un PDF o un archivo de texto 
2. Haga una pregunta al respecto
"""


def process_file(file: AskFileResponse):
    import tempfile

    if file.type == "text/plain":
        Loader = TextLoader
    elif file.type == "application/pdf":
        Loader = PyPDFLoader

    # Specify a custom temporary directory (change to your preferred directory)
    custom_temp_dir = "./tmp"
    with tempfile.NamedTemporaryFile(
        delete=False, dir=custom_temp_dir, suffix=".pdf"
    ) as tempfile:
        tempfile.write(file.content)
        print(tempfile)
        tempfile.flush()
        print(tempfile)
        file_path = tempfile.name
        print(tempfile)
        loader = Loader(file_path)
        documents = loader.load()
        print(documents)
        docs = text_splitter.split_documents(documents)
        for i, doc in enumerate(docs):
            doc.metadata["source"] = f"source_{i}"
        return docs


def get_docsearch(file: AskFileResponse):
    print(f"file loaded is: {file.name}")
    docs = process_file(file)
    # Save data in the user session
    cl.user_session.set("docs", docs)
    # Create a unique namespace for the file

    docsearch = Chroma.from_documents(docs, embeddings)

    return docsearch


@cl.on_chat_start
async def start():
    await cl.Message(content="Ahora puedes chatear con tus pdfs.").send()
    files = None
    while files is None:
        files = await cl.AskFileMessage(
            content=welcome_message,
            accept=["text/plain", "application/pdf"],
            max_size_mb=20,
            timeout=180,
        ).send()

        file = files[0]
        msg = cl.Message(content=f"Procesando: {file.name}")
        await msg.send()

        # No async implementation in the Pinecone client, fallback to sync
        docsearch = await cl.make_async(get_docsearch)(file)

        chain = RetrievalQAWithSourcesChain.from_chain_type(
            ChatOpenAI(temperature=0, streaming=True),
            chain_type="stuff",
            retriever=docsearch.as_retriever(max_tokens_limit=4097),
        )
        msg.content = f"{file.name} Procesado. Puedes empezar a hacer preguntas!"
        await msg.update()

        cl.user_session.set("chain", chain)


@cl.on_message
async def main(message):
    chain = cl.user_session.get("chain")  # type: RetrievalQAWithSourcesChain
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True, answer_prefix_tokens=["FINAL", "ANSWER"]
    )

    cb.answer_reached = True
    res = await chain.acall(message.content, callbacks=[cb])

    answer = res["answer"]
    sources = res["sources"].strip()
    source_elements = []

    # Get the documents from the user session
    docs = cl.user_session.get("docs")
    metadatas = [doc.metadata for doc in docs]
    all_sources = [m["source"] for m in metadatas]

    if sources:
        found_sources = []

        # Add the sources to the message
        for source in sources.split(","):
            source_name = source.strip().replace(".", "")
            # Get the index of the source
            try:
                index = all_sources.index(source_name)
            except ValueError:
                continue
            text = docs[index].page_content
            found_sources.append(source_name)

            # Create the text element referenced in the message
            source_elements.append(cl.Text(content=text, name=source_name))
        if found_sources:
            answer += f"\nSources: {', '.join(found_sources)}"
        else:
            answer += "\nNo sources found"

    if cb.has_streamed_final_answer:
        cb.final_stream.elements = source_elements
        await cb.final_stream.update()
    else:
        await cl.Message(content=answer, elements=source_elements).send()
