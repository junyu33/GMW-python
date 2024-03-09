#!/usr/bin/python3
# alice.py
import socket
import json
import random
import sys
from gates import G

def init_socket(ip, port):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(2)
    s.connect((ip, port))
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


class Alice_GMW:
    def __init__(self, x, sock):
        self.x = x
        self.sock = sock

    def send_number(self, number):
        self.sock.send(str(number).encode())

    def recv_number(self):
        return int(self.sock.recv(1024).decode())

    def run_protocol(self):
        # step1: alice gen xa in [0, 1], xb = x xor xa, sned xb to bob
        xa = random.randint(0, 1)
        xb = self.x ^ xa
        self.send_number(xb)
        
        # step2: bob gen yb in [0, 1], ya = y xor yb, send ya to alice
        ya = self.recv_number()

        # step3: alice gen za in [0, 1], enum f(xb, yb) = za xor G(xa^xb, ya^yb)
        za = random.randint(0, 1)
        f00 = za ^ G(xa^0, ya^0)
        f01 = za ^ G(xa^0, ya^1)
        f10 = za ^ G(xa^1, ya^0)
        f11 = za ^ G(xa^1, ya^1)

        # step4: operate 4 in 1 OT with bob, alice provide f00 to f11, bob provide index according to xb*2+yb
        alice = Alice_nin1_OT(4, [f00, f01, f10, f11], self.sock)
        alice.run_protocol()

        # step5: bob send zb = f(xb, yb) to alice
        zb = self.recv_number()

        # step6: alice and bob reveal G(x, y) = za xor zb
        self.send_number(za)
        z = za ^ zb
        return z


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 alice.py <x> [<ip of bob>] [<port>]')
        exit(1)

    x = int(sys.argv[1])
    port = 12345
    if len(sys.argv) >= 3:
        ip = sys.argv[2]
        if len(sys.argv) >= 4:
            port = int(sys.argv[3])
    else:
        ip = '127.0.0.1'
    sock = init_socket(ip, port)

    # Define the prime number p and generator g
    p = 23
    g = 5


    Alice = Alice_GMW(x, sock)
    res = Alice.run_protocol()
    print('result from Alice: G(x, y) =', res)
    sock.close()
