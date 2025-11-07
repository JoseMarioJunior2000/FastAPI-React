from fastapi import UploadFile

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

async def is_upload_too_large(file: UploadFile) -> bool:
    """
    Verifica se o arquivo enviado via UploadFile ultrapassa 10 MB,
    sem carregar todo o conteúdo na memória.

    Args:
        file (UploadFile): Arquivo recebido via FastAPI (multipart/form-data).

    Returns:
        bool: True se o arquivo for maior que 10 MB, False caso contrário.
    """
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    return size > MAX_FILE_SIZE_BYTES
