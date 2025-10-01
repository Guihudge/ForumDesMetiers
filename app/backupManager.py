import threading
import schedule
import time
from app import app
from app.config import Config
from webdav4.client import Client as ncClient
import datetime

def getWebDavClient() -> ncClient:
    if Config.NC_Client is not None:
        return Config.NC_Client
    else:
        raise ValueError("Not logged in Next Cloud")

def saveDB():
    try:
        ncWebDav = getWebDavClient()
        databasePath = Config.SQLALCHEMY_DATABASE_URI[10:]
        ncWebDav.upload_file(databasePath, f"ForumDesMetier/{datetime.now().year}/app-{datetime.now()}.db")
    except Exception as e:
        Config.BackupErrorLog.append(e)


def startBackupManager(interval=60):
    ceaseContinousRun = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not ceaseContinousRun.is_set():
                schedule.run_pending()
                time.sleep(interval)
    
    continousThread = ScheduleThread()
    continousThread.start()
    return ceaseContinousRun

def stopBackupManager(ceaseContinousRun:threading.Event):
    ceaseContinousRun.set()

def setupBackupManager(savedelay=3600):
    schedule.every(savedelay).seconds.do(saveDB)
    backupThread = startBackupManager()
    return backupThread