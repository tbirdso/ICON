# Python sins, I sin. In the end all is forgiven?
from inspect import getsourcefile
import os.path as path, sys
print("WARNING: I can't really recommend using .")

current_dir = path.dirname(path.abspath(getsourcefile(lambda: 0)))
sys.path.insert(0, current_dir[: current_dir.rfind(path.sep)] + "/src/icon_registration")
