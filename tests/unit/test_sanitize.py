from app.utils.sanitize import escape_html, sanitize_url

def test_escape_html():
    assert escape_html('&<>"') == '&amp;&lt;&gt;&quot;'
    assert escape_html('hello') == 'hello'
    assert escape_html(None) == ''
    assert escape_html('<div>test</div>') == '&lt;div&gt;test&lt;/div&gt;'

def test_sanitize_url():
    assert sanitize_url('https://example.com') == 'https://example.com'
    assert sanitize_url('javascript:alert(1)') == '#'
    assert sanitize_url('data:text/html,<script>') == '#'
    assert sanitize_url('') == '#'
    assert sanitize_url('http://example.com') == 'http://example.com'
    assert sanitize_url('ftp://example.com') == '#'