import time
import os
import requests
import json
import sys, getopt
from os import error
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


DIRECTORY_TO_WATCH = ("C:\\Users\\%s\\Downloads" % os.getenv("username"))
REST_URL = "http://cuckoo.binary.local:7337/tasks"
HEADERS = {"Authorization": "Bearer S1mple_t0Ken"}
SIGNATURE_DATABASE = "C:\\ProgramData\\.clamwin\\db\\malsigs.hdb"


class Watcher:

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()

        self.observer.join()


class Handler(FileSystemEventHandler):

    def on_any_event(self, event):
        if event.is_directory:
            return None

        elif event.event_type == "created":
            # Megabytes
            file_size = os.stat(event.src_path).st_size / (1024 * 1024) 
            if file_size < 5:
                self.check(event.src_path)
    
    def submit(self, file_path):
        head, tail = os.path.split(str(file_path))
        url = REST_URL + "/create/file"

        with open(file_path, "rb") as sample:
            files = {"file": (tail, sample)}
            r = requests.post(url, headers=HEADERS, files=files)
            sample.close()

        task_id = r.json()["task_id"]
        return task_id

    def check(self, file_path):
        task_id = self.submit(file_path)
        url = REST_URL + "/report/" + str(task_id)

        r = requests.get(url, headers=HEADERS)
        while r.status_code != 200:
            time.sleep(5)
            r = requests.get(url, headers=HEADERS)
        
        # a list contains signatures
        sig = json.loads(r.text)["signatures"]
        if bool(sig):
            if os.path.exists(file_path):
                os.system("sigtool --md5 %s >> %s " % (str(file_path), SIGNATURE_DATABASE))
                # os.system("clamscan --remove -d %s %s" % (database.hdb, str(file_path)))
                os.remove(str(file_path))
	

if __name__ == "__main__":
    w = Watcher()
    w.run()