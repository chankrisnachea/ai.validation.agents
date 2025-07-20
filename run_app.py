import os
import sys

os.environ["PYTHONPATH"] = "src"
os.system("streamlit run src/ui/app_chat.py")