import secure_core as sc
from x3dh import KeyBundle, x3dh_initiator, x3dh_responder


def test_x3dh_shared_key_matches():
    bob = KeyBundle()
    bob_bundle = bob.public_bundle()
    alice_ik_priv, alice_ik_pub = sc.generate_keypair()
    sk_alice, ek_pub = x3dh_initiator(alice_ik_priv, bob_bundle)
    sk_bob = x3dh_responder(bob, alice_ik_pub, ek_pub)
    assert sk_alice == sk_bob


def test_x3dh_different_sessions_differ():
    bob = KeyBundle()
    bob_bundle = bob.public_bundle()
    a1_priv, a1_pub = sc.generate_keypair()
    a2_priv, a2_pub = sc.generate_keypair()
    sk1, _ = x3dh_initiator(a1_priv, bob_bundle)
    sk2, _ = x3dh_initiator(a2_priv, bob_bundle)
    assert sk1 != sk2
    