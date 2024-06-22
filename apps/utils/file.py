import base64
import secrets
import mimetypes
from django.core.files.base import ContentFile


def get_content_file_from_base64(data: str):
    if not data:
        return None
    
    content_type, base64_data = data.split(';base64,')
    mimetype = content_type.split(':')[1]
    extension = mimetypes.guess_extension(mimetype)

    if not base64_data.endswith('=='):
        base64_data = base64_data + '=='

    filename = secrets.token_hex(16) + extension
    content_file = ContentFile(base64.b64decode(base64_data.encode()), name=filename)
    return content_file
