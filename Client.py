__author__ = 'ryan'
import socket
import select
import sys
Host = '127.0.0.1'
Port = 4119
#main function
if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try :
        s.connect((Host, Port))
    except :
        print('Unable to connect')
        sys.exit()
    print('Connected to remote host. Start sending messages')
    while True:
        # Wait for file descriptor raise a event
        try:read_sockets= select.select([sys.stdin, s], [], [])[0]
        except:    #do cleanup
            s.sendall(b'close')     #'close' is the hint for server that it should close
            s.close()
            sys.exit()
        for sock in read_sockets:
            #incoming message from remote server
            if sock == s:
                data = sock.recv(1024).decode()
                if data =='close' or not data:
                    print('\nDisconnected from chat server')
                    s.sendall(b'close')
                    s.close()
                    sys.exit()
                else:
                    #print data without adding a '\n'
                    sys.stdout.write(data)
                    sys.stdout.flush()
            #user entered a message
            else:
                #'\r' is the suffix to distinguish normal message from close or other signal
                msg = (raw_input()+'\r').encode()
                s.sendall(msg)
