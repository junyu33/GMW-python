#!/usr/bin/python3
# alice.py
import socket
import json
import random
import sys
from gates import G_compare, G_sum

def init_socket(ip, port):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(60)
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

    def number2list(self, number):
        res = []
        for i in range(comm_bit):
            res.append(number & 1)
            number >>= 1
        return res

    def list2number(self, l):
        res = 0
        for i in range(comm_bit):
            res += l[i] * (2**i)
        return res

    def run_protocol(self):
        # step1: alice gen xa in [0, 2**comm_bit-1], xb = x xor xa, sned xb to bob
        xa = random.randint(0, 2**comm_bit-1)
        xb = self.x ^ xa
        self.send_number(xb)
        
        # step2: bob gen yb in [0, 2**comm_bit-1], ya = y xor yb, send ya to alice
        ya = self.recv_number()

        # step3: alice gen za in [0, 1], enum f(xb, yb) = za xor G(xa^xb, ya^yb)
        za = random.randint(0, 1)

        f = []

        for possible_xb in range(2**comm_bit):
            for possible_yb in range(2**comm_bit):
                xa_xor_xb_list = self.number2list(xa^possible_xb)
                ya_xor_yb_list = self.number2list(ya^possible_yb)
                f.append(za ^ G_compare(xa_xor_xb_list, ya_xor_yb_list))

        # step4: operate 4**comm_bit in 1 OT with bob, alice provide f00 to f{2**comm_bit-1}{2**comm_bit-1}, bob provide index according to xb*(2**comm_bit)+yb
        alice = Alice_nin1_OT(4**comm_bit, f, self.sock)
        alice.run_protocol()

        # step5: bob send zb = f(xb, yb) to alice
        zb = self.recv_number()

        # step6: alice and bob reveal G(x, y) = za xor zb
        self.send_number(za)
        z = za ^ zb
        return z

    def run_sum_protocol(self):
        # step1: alice gen xa in [0, 2**comm_bit-1], xb = x xor xa, sned xb to bob
        xa = random.randint(0, 2**comm_bit-1)
        xb = self.x ^ xa
        self.send_number(xb)
        
        # step2: bob gen yb in [0, 2**comm_bit-1], ya = y xor yb, send ya to alice
        ya = self.recv_number()

        # step3: alice gen za in [0, 1], enum f(xb, yb) = za xor G(xa^xb, ya^yb)
        za = random.randint(0, 2**comm_bit-1)

        f = []

        for possible_xb in range(2**comm_bit):
            for possible_yb in range(2**comm_bit):
                xa_xor_xb_list = self.number2list(xa^possible_xb)
                ya_xor_yb_list = self.number2list(ya^possible_yb)
                sum_list = G_sum(xa_xor_xb_list, ya_xor_yb_list)
                f.append(za ^ self.list2number(sum_list))

        # step4: operate 4**comm_bit in 1 OT with bob, alice provide f00 to f{2**comm_bit-1}{2**comm_bit-1}, bob provide index according to xb*(2**comm_bit)+yb
        alice = Alice_nin1_OT(4**comm_bit, f, self.sock)
        alice.run_protocol()

        # step5: bob send zb = f(xb, yb) to alice
        zb = self.recv_number()

        # step6: alice and bob reveal G(x, y) = za xor zb
        self.send_number(za)
        z = za ^ zb
        return z


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 alice.py <mode> <x> [<ip of bob>] [<port>]')
        exit(1)

    mode = sys.argv[1]
    x = int(sys.argv[2])
    port = 12345
    if len(sys.argv) >= 4:
        ip = sys.argv[3]
        if len(sys.argv) >= 5:
            port = int(sys.argv[4])
    else:
        ip = '127.0.0.1'
    sock = init_socket(ip, port)

    # Define the prime number p and generator g
    p = 998244353
    g = 3
    comm_bit = 5


    Alice = Alice_GMW(x, sock)
    if mode == 'c': 
        res = Alice.run_protocol()
    elif mode == 'a':
        res = Alice.run_sum_protocol()
    else:
        print('mode error')
        exit(1)
    print('result from Alice: G(x, y) =', res)
    sock.close()
