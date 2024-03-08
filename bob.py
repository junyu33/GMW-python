#!/usr/bin/python3           
# bob.py
import socket
import random
import json

# pre-defined values
p = 23
g = 5

# which one bob choose
i = random.randint(0, 2)
# key
k = random.randint(1, p-1)

def bob_init():
    # Create a socket object
    s = socket.socket()
    # help reuse the port immediately
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # set a timeout of 2 second
    s.settimeout(2)  
    # Define the port on which you want to listen
    port = 12345
    # Bind to the port
    s.bind(('127.0.0.1', port))
    # Put the socket into listening mode
    s.listen(5)
    # Wait for a connection from Alice
    c, addr = s.accept()
    print('Got connection from', addr)
    return c

def bob_send(s, number):
    s.send(str(number).encode())

def bob_recv(s):
    return int(s.recv(1024).decode())

def alice_send_json(s, json):
    s.send(json.encode())

def alice_recv_json(s):
    return json.loads(s.recv(1024).decode())


bob_sock = bob_init()


# STEP 1: Alice -> Bob : g**s 
gs = bob_recv(bob_sock)

# STEP 2: generate Li = g**k when i = 0, g**(s-k) otherwise
Li = 0
if i == 0:
    Li = pow(g, k, p)
else:
    Li = gs * pow(g, -k, p) % p

# STEP 3: Bob -> Alice : Li
bob_send(bob_sock, Li)

# STEP 5: Alice -> Bob : C0, C1
C0C1 = alice_recv_json(bob_sock)
C0 = C0C1[0]
C1 = C0C1[1]

# STEP 6: Bob decrypt v_i
# if i = 0, v0 = C0[0] ** k ^ C0[1]
# if i = 1, v1 = C1[0] ** k ^ C1[1]
v = 0
if i == 0:
    v = pow(C0[0], k, p) ^ C0[1]
else:
    v = pow(C1[0], k, p) ^ C1[1]
print('v_' + str(i) + ' =', v)

# Close the connection
bob_sock.close()

