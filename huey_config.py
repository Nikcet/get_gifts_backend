import os
from huey import SqliteHuey
from dotenv import load_dotenv
load_dotenv()

TASKBASE_URL = os.getenv("TASKBASE_URL")
huey = SqliteHuey(filename=TASKBASE_URL, immediate=False)