import html
from urllib.parse import urlparse

def escape_html(text: str) -> str:
    if not text:
        return ""
    return html.escape(str(text), quote=True)

def sanitize_url(url: str) -> str:
    if not url:
        return "#"
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return "#"
        return url
    except Exception:
        return "#"