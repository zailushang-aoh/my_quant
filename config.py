import os
from dotenv import load_dotenv

# 从环境变量读取凭据，避免在代码中明文写入密码
load_dotenv()
TQ_USERNAME = os.getenv("TQ_USERNAME")
TQ_PASSWORD = os.getenv("TQ_PASSWORD")

