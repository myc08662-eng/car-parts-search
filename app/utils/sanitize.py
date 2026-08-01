import html

def escape_html(text: str) -> str:
    if not text:
        return ""
    return html.escape(str(text), quote=True)

def sanitize_url(url: str) -> str:
    if not url:
        return "#"
    if url.lower().startswith(("javascript:", "data:")):
        return "#"
    return url