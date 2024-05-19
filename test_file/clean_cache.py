import pathlib
import shutil

_ = [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]