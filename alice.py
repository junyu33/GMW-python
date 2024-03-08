#!/usr/bin/python3
# alice.py
import socket
import json
import random

def init_socket(port):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(2)
    s.connect(('127.0.0.1', port))
    return s

class Alice_2in1_OT:
    def __init__(self, p, g, v0, v1, sock):
        self.p = p
        self.g = g
        self.s = random.randint(1, p-1)
        self.r0 = random.randint(1, p-1)
        self.r1 = random.randint(1, p-1)
        self.v0 = v0
        self.v1 = v1
        self.sock = sock

    def inv(self, x):
        return pow(x, -1, self.p)

    def send_number(self, number):
        self.sock.send(str(number).encode())

    def recv_number(self):
        return int(self.sock.recv(1024).decode())

    def send_json(self, data):
        self.sock.send(json.dumps(data).encode())

    def recv_json(self):
        return json.loads(self.sock.recv(1024).decode())

    def run_protocol(self):
        # STEP 1: Alice -> Bob: gs = g**s
        self.send_number(pow(self.g, self.s, self.p))

        # STEP 3: Bob -> Alice: Li
        Li = self.recv_number()

        # Step 4: generate C0, C1
        C0 = (pow(self.g, self.r0, self.p), pow(Li, self.r0, self.p) ^ self.v0)
        C1 = (pow(self.g, self.r1, self.p), pow(pow(self.g, self.s, self.p) * self.inv(Li) % self.p, self.r1, self.p) ^ self.v1)

        # Step 5: Alice -> Bob: C0, C1
        self.send_json([C0, C1])


class Alice_nin1_OT:
    def __init__(self, n, x : list, sock):
        self.n = n
        self.x = [0] # add a dummy value to make the index start from 1
        self.x.extend(x)
        self.k = [0]
        for i in range(self.n):
            self.k.append(random.randint(0, 1))
        self.sock = sock

    def run_protocol(self):
        # alice and bob perform the 2-in-1 OT protocol for n times
        v0 = self.x[0] 
        for j in range(1, self.n + 1):
            # v0 = k0 xor k1 xor ... xor k_{j-1} xor x[j]
            v0 ^= self.k[j-1] ^ self.x[j-1] ^ self.x[j] 
            # v1 = k[j]
            v1 = self.k[j]

            alice = Alice_2in1_OT(p, g, v0, v1, self.sock) # avoid port conflict
            alice.run_protocol()


# Define the prime number p and generator g
p = 23
g = 5

sock = init_socket(20000)

Alice = Alice_nin1_OT(4, [1, 0, 1, 0], sock)
Alice.run_protocol()


#alice = Alice_2in1_OT(p, g, 4, 0, sock)
#alice.run_protocol()
#alice = Alice_2in1_OT(p, g, 4, 0, sock)
#alice.run_protocol()

