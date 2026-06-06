import secure_core as sc


class KeyBundle:
    def __init__(self):
        self.ik_priv, self.ik_pub = sc.generate_keypair()
        self.spk_priv, self.spk_pub = sc.generate_keypair()
        self.opk_priv, self.opk_pub = sc.generate_keypair()

    def public_bundle(self):
        return {
            "ik": self.ik_pub,
            "spk": self.spk_pub,
            "opk": self.opk_pub,
        }


def x3dh_initiator(alice_ik_priv, bob_bundle):
    ek_priv, ek_pub = sc.generate_keypair()
    dh1 = sc.dh(alice_ik_priv, bob_bundle["spk"])
    dh2 = sc.dh(ek_priv, bob_bundle["ik"])
    dh3 = sc.dh(ek_priv, bob_bundle["spk"])
    dh4 = sc.dh(ek_priv, bob_bundle["opk"])
    shared_key = sc.kdf_sk(dh1 + dh2 + dh3 + dh4)
    return shared_key, ek_pub


def x3dh_responder(bob, alice_ik_pub, alice_ek_pub):
    dh1 = sc.dh(bob.spk_priv, alice_ik_pub)
    dh2 = sc.dh(bob.ik_priv, alice_ek_pub)
    dh3 = sc.dh(bob.spk_priv, alice_ek_pub)
    dh4 = sc.dh(bob.opk_priv, alice_ek_pub)
    shared_key = sc.kdf_sk(dh1 + dh2 + dh3 + dh4)
    return shared_key