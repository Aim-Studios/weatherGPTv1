import os
import sys

# This forces the pip install command to target this exact IDLE environment
#os.system(f'"{sys.executable}" -m pip install python-dotenv openai')

from dotenv import load_dotenv
from openai import OpenAI
