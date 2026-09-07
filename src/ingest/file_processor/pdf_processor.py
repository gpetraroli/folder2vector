from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pymupdf as fitz
import base64

from folder2vector.config import CHUNK_OVERLAP, CHUNK_SIZE, OCR_MODEL, OLLAMA_URL

from .file_processor_interface import FileProcessorInterface


class PDFProcessor(FileProcessorInterface):
    def __str__(self) -> str:
        return "PDFProcessor"

    def process(self, file_path: str) -> None:
        splits = self.split_pdf_document(file_path)

        self.embed_documents(file_path, splits)

    def split_pdf_document(self, file_path: str) -> list[Document]:
        loader = PyPDFLoader(file_path)

        docs = loader.load()

        if not any(doc.page_content.strip() for doc in docs):
            docs = self._ocr_pdf(file_path)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        return text_splitter.split_documents(docs)

    def _ocr_pdf(self, file_path: str) -> list[Document]:
        print(f"OCRing PDF: {file_path}")
        llm = ChatOllama(
            model=OCR_MODEL,
            base_url=OLLAMA_URL,
            temperature=0,
        )

        docs: list[Document] = []

        with fitz.open(file_path) as doc:
            for page_num, page in enumerate(doc):
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                image_b64 = base64.b64encode(pix.tobytes()).decode("ascii")

                response = llm.invoke([
                    HumanMessage(content=[
                        {"type": "text", "text": "Text Recognition:"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_b64}"
                            },
                        },
                    ])
                ])

                text = response.content.strip()
                if text:
                    docs.append(Document(
                        page_content=text,
                        metadata={"source": file_path, "page": page_num + 1},
                    ))

        return docs
