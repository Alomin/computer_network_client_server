computer_network_client_server
==============================
Executable files built for csee4119 computer network.

Follow these steps to load and debug this project built on the command line. 

1. Server is constructed by multi-threading. Main thread to accept new connection; overwrite subclass ‘Client’ thread for clients connecting in; a counter thread to 
inspect the ‘TIME_OUT’ clients, because any other threads are blocking in recv() or accept(). For the same reason, if ‘ctrl +c’ is pressed, I choose to stop threads by
sending a message to inform client and wait for the response. Recv() rewritten has a
really good function to call cleanup() when close signal or no message is received.
Any message except signal message has a ‘r’ to distinguish, while no message only happen when the connection is cut off.
Client has the same mechanism for ‘ctrl+c’.But python is really not friendly enough to multi-threading, the Client is achieved by select(). It takes file descriptor as args.
When there is a event, the file descriptors are returned.

2. Pycharm 3.4 interpretor python 2.7.5 macbook unix.

3. Only three files: Sever.py, Client.py and user_pass. Run them in command line directly.
Just in case, if the port number is occupied, I hope you could open my source code and make a little change of the ‘Port’. It’s right on the top, a piece of cake. The server listens on all the address this computer have access to. If you want to try the real IP, don’t forget to open both the Client.py and make a little change.

4. $ python2.7 ~/Server.py   ~ indicates the path
   $ python2.7 ~/Client.py

5.a.offline messaging
  b.command invisible   Switch the state invisible or not. When invisible, can’t be seen by who else and wholasthr.
  c.command showrecord The server keep all the records this user have including all the offline broadcast and offline message.
