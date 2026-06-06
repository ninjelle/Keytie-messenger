import secure_core as sc


class Header:
    def __init__(self, dh_pub, pn, n):
        self.dh_pub = dh_pub
        self.pn = pn
        self.n = n

    def to_bytes(self):
        return self.dh_pub + self.pn.to_bytes(4, "big") + self.n.to_bytes(4, "big")


class DoubleRatchet:
    def __init__(self):
        self.dhs_priv = None
        self.dhs_pub = None
        self.dhr = None
        self.rk = None
        self.cks = None
        self.ckr = None
        self.ns = 0
        self.nr = 0
        self.pn = 0

    @classmethod
    def init_alice(cls, shared_key, bob_dh_pub):
        state = cls()
        state.dhs_priv, state.dhs_pub = sc.generate_keypair()
        state.dhr = bob_dh_pub
        dh_out = sc.dh(state.dhs_priv, state.dhr)
        state.rk, state.cks = sc.kdf_rk(shared_key, dh_out)
        return state

    @classmethod
    def init_bob(cls, shared_key, bob_dh_keypair):
        state = cls()
        state.dhs_priv, state.dhs_pub = bob_dh_keypair
        state.rk = shared_key
        return state

    def encrypt(self, plaintext):
        self.cks, mk = sc.kdf_ck(self.cks)
        header = Header(self.dhs_pub, self.pn, self.ns)
        self.ns += 1
        ciphertext = sc.encrypt(mk, plaintext, header.to_bytes())
        return header, ciphertext

    def decrypt(self, header, ciphertext):
        if header.dh_pub != self.dhr:
            self._dh_ratchet(header)
        self.ckr, mk = sc.kdf_ck(self.ckr)
        self.nr += 1
        return sc.decrypt(mk, ciphertext, header.to_bytes())

    def _dh_ratchet(self, header):
        self.pn = self.ns
        self.ns = 0
        self.nr = 0
        self.dhr = header.dh_pub
        self.rk, self.ckr = sc.kdf_rk(self.rk, sc.dh(self.dhs_priv, self.dhr))
        self.dhs_priv, self.dhs_pub = sc.generate_keypair()
        self.rk, self.cks = sc.kdf_rk(self.rk, sc.dh(self.dhs_priv, self.dhr))