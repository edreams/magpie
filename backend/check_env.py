import sys
import os
from dotenv import load_dotenv
load_dotenv()
print(os.getenv('CHROMEDRIVER_PATH'))