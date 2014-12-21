__author__ = 'ryan'
import socket
import threading
import sys
import time

#init datasheet
Host = ''
Port = 4119
TIME_OUT = 1800
BLOCK_TIME = 60
LAST_HOUR = 3600
threads = []
blacklist = []
timerecord = {}
privatemsg = []

with open("user_pass.txt", "r") as f:
    usrinfo = f.read().split()
usrdict = dict(zip(usrinfo[::2], usrinfo[1::2]))
messagerecord = {}
for usr in usrdict:messagerecord[usr]=[]

#subclass thread, one for a client
class Client(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        threads.append(self)
        self.login = False
        self.lastactive = time.time()
        self.s = socket
        self.addr = socket.getpeername()
        self.invi = False
        print('connected with '+self.addr[0]+':'+str(self.addr[1]))

    def run(self):
        self.usr = self.Login()
        self.login = True
        timerecord[self.usr] = 0
        self.send('Welcome\n')
        #send the private message stored
        for line in privatemsg:
            if line[0] == self.usr: self.send(line[1])
            privatemsg.remove(line)
        while True:
            self.send('Command:')
            rawmsg = self.recv()
            cmd, msg = (rawmsg+' ').split(' ', 1)
            if cmd == 'logout':self.cleanup()
            elif cmd == 'whoelse':self.whoelse()
            elif cmd == 'wholasthr':self.wholasthr()
            elif cmd == 'broadcast':self.broadcast(msg)
            elif cmd == 'message':self.message(msg)
            elif cmd == 'invisible':self.invisible()
            elif cmd == 'showrecord':self.showrecord()
            else:self.send('Wrong command,please try again\nCommand:')
    #prefix '\r', no prefix for sys command signal. e.g. b'close' means exit()
    def send(self, msg):
        msg = ('\r'+msg).encode()
        try:self.s.sendall(msg)
        except:return
    #inspect if the connection is still good, also receive the close signal. Strip our prefix or suffix '\r'
    def recv(self):
        msg = self.s.recv(1024).decode()
        if msg == 'close' or not msg:
            self.cleanup()
        self.lastactive = time.time()
        return msg.strip('\r')
    def Login(self):
        #branches:active,block,pass,3wrong,namewrong
        self.send('Username:')
        usr = self.recv()
        if [usr, self.addr[0]] in blacklist:self.cleanup() #is blocked
        for t in threads:#is login
            if t.login and t.usr == usr:
                self.cleanup()
        for i in range(3):#prompt password
            self.send('Password:')
            pwd = self.recv()
            if usrdict.get(usr) == pwd:return usr #login
        if usr in usrdict:#login failed, add to blacklist if possible
            self.s.sendall(b'close')
            blacklist.append([usr, self.addr[0]])
            time.sleep(BLOCK_TIME)
            blacklist.remove([usr, self.addr[0]])
        self.cleanup()#not in usrlist,discard
    def cleanup(self):
        self.s.sendall(b'close')
        #record logout time with a dictionary,but self.lastactive is for time expire
        if self.login:timerecord[self.usr] = time.time()
        self.login = False
        self.invi = False
        self.s.close()
        threads.remove(self)
        sys.exit()
    def whoelse(self):
        msg = ""
        for t in threads:
            if t.login and t != self and not t.invi: msg += t.usr +' '
        self.send(msg+'\n')
    def wholasthr(self):
        now, msg = time.time(), ''
        for t in threads:
            if t.login and t != self and not t.invi: msg += t.usr +' '
        for usr in timerecord:
            if timerecord[usr] + LAST_HOUR > now:msg += usr +' '
        self.send(msg+'\n')
    def broadcast(self, msg):
        messagerecord[self.usr].append('broadcast '+msg+'\nCommand:')#a little bit tricky to overwrite Cammand:
        for usr in messagerecord:
            if usr != self.usr:messagerecord[usr].append(self.usr+':'+msg+'\nCommand:')
        for t in threads:
            if t.login and t != self:
                t.send(self.usr+':'+msg+'\nCommand:')

    def message(self, rawmsg):
        receiver, msg = (rawmsg+' ').split(' ', 1)
        if receiver in usrdict:
            messagerecord[self.usr].append('message '+rawmsg+'\nCommand:')
            messagerecord[receiver].append(self.usr+':'+msg+'\nCommand:')
            for t in threads:
                if t.login and t.usr == receiver:
                    t.send(self.usr+':'+msg+'\nCommand:')
                    return
            privatemsg.append([receiver, self.usr+':'+msg+'\nCommand:'])


    def invisible(self):
        if self.invi: self.invi = False
        else: self.invi = True
    def showrecord(self):
        for line in messagerecord[self.usr]:
            self.send(line)

#Daemon thread for auto-disconnect
def count():
    try:
        while True:
            time.sleep(3)
            for t in threads:
                if time.time() - t.lastactive > TIME_OUT:
                    t.s.sendall(b'close')
    except:sys.exit()
timeout = threading.Thread(target = count)
timeout.setDaemon(True)
timeout.start()
#start listen
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:s.bind((Host, Port))
except:
    print('port already in use')
    sys.exit()
s.listen(5)
#main thread to accept new client
while True:
    try:conn = s.accept()[0]
    except:break
    Client(conn).start()
#client close first. Don't worry about bad socket, because it has a self-clean mechanism
for t in threads:
    t.s.sendall(b'close')

print('server close successfully')


