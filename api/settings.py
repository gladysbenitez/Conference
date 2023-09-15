from starlette.config import Config

config = Config(".env")
MONGODB_URL = config("MONGODB_URL", default="no-url")
MONGO_DB = config("MONGO_DB")
SESSION_SECRET_KEY = config("SESSION_SECRET_KEY")
