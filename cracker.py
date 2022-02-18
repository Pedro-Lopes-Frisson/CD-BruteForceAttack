import string
import threading
import time
charlist = string.ascii_uppercase + string.ascii_lowercase + string.digits

class passGening(threading.Thread):
    def __init__(self, increment, Max_size,ID,current ):
        threading.Thread.__init__(self)
        self.inc = increment
        self.Max_size = Max_size
        self.ID = ID
        self.current = current
        self.passWordStore = list()
        global charlist
        self.char = charlist[:]
        self.pos = 0

    def run (self):
        for i in range(0, 9000000):
            self.passWordStore.append(self.getNext())


    def givePass(self):
        temp = self.passWordStore[self.pos]
        self.pos = self.pos + 1
        if self.pos > len(self.passWordStore):
 # Podem estar a ser geradas passes ainda
            self.pos=0
        return temp

    def getNext(self):
        global charlist
        count = 0
        nxt = ""
        if(self.current == ""):
            return self.char[self.inc-1+self.ID]
        else:
            for i in range(len(self.current)-1, -1, -1):
                ind = charlist.index(self.current[i])
                if count == 0:
                    if ind+self.inc >= len(charlist):
                        nxt = self.char[(ind+self.inc)%len(charlist)] + nxt
                        self.inc = 1
                    else:
                        count = 1
                        nxt =  self.char[ind+self.inc] + nxt
                        self.inc = 1
                else:
                    nxt = self.current[i] + nxt
            if count == 0:
                nxt = self.char[0] + nxt
            return nxt


def threadFunc(ID):
    for i in range(0, 9000000):
        pswd = getNext( offset, Max_size, ID, pswd)                          # Password list to try on
        print(pswd)


if __name__ == "__main__":
    offset = 1                                               # Number of Slaves
    ID = 0                                                        # Id of slave
    Max_size = 8
    pswd = "" # Max size of passwordds

    for t in  threads_launched:
        t.join()
        print(f"thread {t} acabou de executar")
