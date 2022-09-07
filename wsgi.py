import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# 通过load_dotenv ，就可以像访问系统环境变量一样访问.env文件中的变量了，
# 比如通过 os.genenv(key, default=None)
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from bluelog import create_app  # noqa

app = create_app('production')
