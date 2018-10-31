#!/bin/env python3

import subprocess
import threading
def callSubProcess(processCmd, shell = True):
    proc = subprocess.Popen(processCmd, shell=shell, stdout=None)
    retCode = proc.wait()
    print(threading.currentThread().getName(), retCode)



if __name__ == "__main__":
    #
    cmdList = ["tree", "/home/nan/github"]
    # callSubProcess(cmdList, shell= False)
    thread1 = threading.Thread(target=callSubProcess, args=(cmdList, False,), name="Thread_cmdList")

    cmd = "tree ~ | grep py"
    # callSubProcess(cmd, shell= True)
    thread2 = threading.Thread(target=callSubProcess, args=(cmd, True,), name="Thread_cmd")

    print(threading.currentThread().getName(), "Main Runing")
    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
    print(threading.currentThread().getName(), "Main Stop")
