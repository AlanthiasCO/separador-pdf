import io
import zipfile

import fitz
import streamlit as st


st.set_page_config(
    page_title="Separador de PDF para PNG",
    page_icon="📄",
    layout="centered",
)

st.title("Separador de PDF para PNG")
st.write(
    "Carregue um arquivo PDF para converter todas as paginas em imagens PNG "
    "e baixar o resultado em um arquivo ZIP."
)


def pdf_to_zip(pdf_bytes: bytes, zoom: float = 2.0) -> tuple[io.BytesIO, int]:
    """Converte todas as paginas do PDF em PNG e devolve um ZIP em memoria."""
    zip_buffer = io.BytesIO()

    with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf_document:
        total_pages = len(pdf_document)

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            matrix = fitz.Matrix(zoom, zoom)

            for page_index, page in enumerate(pdf_document, start=1):
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                image_bytes = pixmap.tobytes("png")
                filename = f"pagina_{page_index:03d}.png"
                zip_file.writestr(filename, image_bytes)

    zip_buffer.seek(0)
    return zip_buffer, total_pages


uploaded_file = st.file_uploader("Selecione um arquivo PDF", type=["pdf"])

if uploaded_file is not None:
    st.info("Arquivo carregado com sucesso. Clique no botao abaixo para processar.")

    if st.button("Converter PDF em PNG"):
        pdf_bytes = uploaded_file.getvalue()

        try:
            with st.spinner("Convertendo paginas..."):
                zip_buffer, total_pages = pdf_to_zip(pdf_bytes)

            base_name = uploaded_file.name.rsplit(".", 1)[0]
            zip_name = f"{base_name}_png.zip"

            st.success(f"Conversao concluida. {total_pages} pagina(s) processada(s).")
            st.download_button(
                label="Baixar ZIP com as imagens",
                data=zip_buffer.getvalue(),
                file_name=zip_name,
                mime="application/zip",
            )
        except Exception as error:
            st.error(
                "Nao foi possivel processar o PDF. "
                f"Verifique se o arquivo esta valido. Detalhes: {error}"
            )
