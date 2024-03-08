#!/usr/bin/python3           
# bob.py
import socket
import random
import json

def init_socket(port):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(2)
    s.bind(('127.0.0.1', port))
    s.listen(5)
    c, addr = s.accept()
    print('Got connection from', addr)
    return c

class Bob_2in1_OT:
    def __init__(self, p, g, i, sock):
        self.p = p
        self.g = g
        self.i = i
        self.k = random.randint(1, p-1)
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
        # STEP 1: Alice -> Bob : g**s 
        gs = self.recv_number()

        # STEP 2: generate Li = g**k when i = 0, g**(s-k) otherwise
        if self.i == 0:
            Li = pow(self.g, self.k, self.p)
        else:
            Li = gs * pow(self.g, -self.k, self.p) % self.p

        # STEP 3: Bob -> Alice : Li
        self.send_number(Li)

        # STEP 5: Alice -> Bob : C0, C1
        C0C1 = self.recv_json()
        C0 = C0C1[0]
        C1 = C0C1[1]

        # STEP 6: Bob decrypt v_i
        if self.i == 0:
            v = pow(C0[0], self.k, self.p) ^ C0[1]
        else:
            v = pow(C1[0], self.k, self.p) ^ C1[1]
        # print('v_' + str(self.i) + ' =', v)
        return v

class Bob_nin1_OT:
    def __init__(self, n, i, sock):
        self.n = n
        self.i = i
        self.sock = sock
    
    def run_protocol(self):
        # alice and bob perform the 2-in-1 OT protocol for n times
        k = [] 
        # if j == i, bob choose k0 xor k1 xor ... xor k_{j-1} xor x[j]
        # otherwise, bob choose kj
        for j in range(1, self.n + 1):
            if j == self.i:
                bob = Bob_2in1_OT(p, g, 0, self.sock) 
                k.append(bob.run_protocol())
            else:
                bob = Bob_2in1_OT(p, g, 1, self.sock)
                k.append(bob.run_protocol())
        
        # with a little calculation we know the xor sum of first i elements of k is x[i]
        xi = 0
        for j in range(0, self.i):
            xi ^= k[j]
        return xi

# Define the prime number p and generator g
p = 23
g = 5

sock = init_socket(20000)

Bob = Bob_nin1_OT(4, 3, sock)
res = Bob.run_protocol()
print(res)

#bob = Bob_2in1_OT(p, g, 0, sock)
#res = bob.run_protocol()
#print(res)
#bob = Bob_2in1_OT(p, g, 0, sock)
#res = bob.run_protocol()
#print(res)
