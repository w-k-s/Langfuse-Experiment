from importlib import resources
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langfuse_experiment.app import AppContext


def index_document(app: AppContext, file_name):
    try:
        path = resources.files("kb").joinpath(file_name)
        loader = DoclingLoader(
            file_path=str(
                path
            ),  # If you pass the path instance directly, the instance is returned as-is in the metadata which chroma rejects.
            export_type=ExportType.MARKDOWN,
        )
        docs = loader.load()

        assert (
            len(docs) == 1
        ), "Index function doesn't handle multiple documents, Actual docs: {}".format(
            len(docs)
        )
        # Docling returns one Document per file when export_type=MARKDOWN
        full_markdown = docs[0].page_content
        source_metadata = docs[0].metadata

        # Define header levels to split on (matches markdown headings Docling emits)
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]

        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False,  # keep header text inside the chunk content
        )

        header_split_docs = markdown_splitter.split_text(full_markdown)

        # Further split large sections by size (some sections be too long for the context window)

        char_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
        )
        final_chunks = char_splitter.split_documents(header_split_docs)

        for chunk in final_chunks:
            chunk.metadata.update(source_metadata)

        _ids = app.chroma.add_documents(final_chunks)
        print("Indexing completed: {} chunks".format(len(_ids)))

    except Exception as e:
        raise RuntimeError("Indexing {} failed".format(file_name)) from e
