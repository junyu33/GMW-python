#!/usr/bin/python3
# alice.py
import socket
import random
import json

# Define the prime number p
p = 23
# Generate a generator g in Z_p field
g = 5

# values in alice
v0 = 12
v1 = 21
# keys
s = random.randint(1, p-1)
r0 = random.randint(1, p-1)
r1 = random.randint(1, p-1)

def inv(x, p):
    return pow(x, -1, p)

def alice_init():
    # Create a socket object
    s = socket.socket()
    # help reuse the port immediately
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # set a timeout of 2 second
    s.settimeout(2)  
    # Define the port on which you want to connect
    port = 12345
    # Connect to the server on local computer
    s.connect(('127.0.0.1', port))
    return s

def alice_send(s, number):
    s.send(str(number).encode())

def alice_recv(s):
    return int(s.recv(1024).decode())

def alice_send_json(s, json):
    s.send(json.encode())

def alice_recv_json(s):
    return json.loads(s.recv(1024).decode())

alice_sock = alice_init()


# STEP 1: Alice -> Bob: gs = g**s
alice_send(alice_sock, pow(g, s, p))

# STEP 3: Bob -> Alice: Li
Li = alice_recv(alice_sock)

# Step 4: generate C0, C1
# C0 = (g**r0, Li**r0 ^ v0)
# C1 = (g**r1, (gs/Li)**r1 ^ v1)
C0 = (pow(g, r0, p), pow(Li, r0, p) ^ v0)
C1 = (pow(g, r1, p), pow(pow(g, s, p) * inv(Li, p) % p, r1, p) ^ v1)

# Step 5: Alice -> Bob: C0, C1
alice_send_json(alice_sock, json.dumps([C0, C1]))

# Close the connection
alice_sock.close()

