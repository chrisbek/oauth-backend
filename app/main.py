from mangum import Mangum
from app.config import on_startup
from app.config.config import Container

Container()
app = on_startup.init()
handler = Mangum(app)
