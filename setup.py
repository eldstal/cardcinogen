import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
                      "packages": ["os"],
                      "include_files": [ "cards-against-humanity", "concept", "fluxx" ]
                    }

base=None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "cardcinogen",
        version = "0.1",
        description = "Tabletop Simulator deck generator for text-card type games",
        options = {"build_exe": build_exe_options},
        executables = [Executable("Cardcinogen.py", base=base)])
