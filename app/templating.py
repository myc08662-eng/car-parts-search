from fastapi.templating import Jinja2Templates
import os

# Папка с HTML-шаблонами находится в app/templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))