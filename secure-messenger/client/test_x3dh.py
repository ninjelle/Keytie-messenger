import secure_core as sc
from x3dh import KeyBundle, x3dh_initiator, x3dh_responder
from ratchet import DoubleRatchet

bob = KeyBundle()
bob_bundle = bob.public_bundle()

alice_ik_priv, alice_ik_pub = sc.generate_keypair()

sk_alice, ek_pub = x3dh_initiator(alice_ik_priv, bob_bundle)
sk_bob = x3dh_responder(bob, alice_ik_pub, ek_pub)

print("Obshchiy klyuch sovpal:", sk_alice == sk_bob)

alice = DoubleRatchet.init_alice(sk_alice, bob_bundle["spk"])
bob_r = DoubleRatchet.init_bob(sk_bob, (bob.spk_priv, bob.spk_pub))

h1, c1 = alice.encrypt(b"Privet cherez X3DH!")
print("Bob poluchil:", bob_r.decrypt(h1, c1).decode())