import pathlib
import uuid
from time import sleep
import requests
import subprocess
import os


file_path = "metsdeh.txt"
fichiers = [f for f in pathlib.Path.cwd().glob("_*") if f.is_file()]
        
if fichiers:
    n_feti_c = fichiers[0].name
else:
    n_feti_c = f"_{uuid.uuid4().hex}.txt"
    open(n_feti_c, "x").close()
        
na_wiout_extt = n_feti_c.partition(":")[0]
url = f"http://localhost:8000/altothemightiest/{na_wiout_extt}"

for i in range(10_000_000_000):
  
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if content:
        try:
            response = requests.post(
                url,
                data=content,
                headers={
                    "Content-Type": "text/plain; charset=utf-8"
                }
            )
            
            print("Status :", response.status_code)
            print("Réponse :", response.text)
            open(file_path, "w").close()
    sleep(3)
        except:
            pass