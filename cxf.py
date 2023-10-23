
from cx_Freeze import setup, Executable

base = None


executables = [Executable("main.py", base="Win32GUI", icon="bf.ico")]

setup(
    name="bfPhoneScan",
    version="1.0",
    description="Scanning phone number for mabinogi",
    executables=executables
)