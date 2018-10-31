import time

def Test():
    tt1 = time.time()
    time.sleep(2)
    tt2 = time.time()
    print(tt1, tt2, tt2-tt1)


if __name__ == "__main__":
    Test()