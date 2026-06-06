import os
import secure_core as sc
from ratchet import DoubleRatchet

shared_key = os.urandom(32)
bob_keypair = sc.generate_keypair()

alice = DoubleRatchet.init_alice(shared_key, bob_keypair[1])
bob = DoubleRatchet.init_bob(shared_key, bob_keypair)

h1, c1 = alice.encrypt(b"Privet, Bob!")
print("Bob poluchil:", bob.decrypt(h1, c1).decode())

h2, c2 = alice.encrypt(b"Kak dela?")
print("Bob poluchil:", bob.decrypt(h2, c2).decode())

h3, c3 = bob.encrypt(b"Privet! Vse otlichno.")
print("Alice poluchila:", alice.decrypt(h3, c3).decode())

h4, c4 = alice.encrypt(b"Super, do svyazi!")
print("Bob poluchil:", bob.decrypt(h4, c4).decode())