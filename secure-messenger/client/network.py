import base64

import requests

from x3dh import KeyBundle, x3dh_initiator, x3dh_responder
from ratchet import DoubleRatchet, Header


def _b64(data):
    return base64.b64encode(data).decode()


def _unb64(text):
    return base64.b64decode(text)


class Messenger:
    def __init__(self, username, server_url="http://127.0.0.1:8000"):
        self.username = username
        self.server_url = server_url
        self.bundle = KeyBundle()
        self.sessions = {}

    def register(self):
        pub = self.bundle.public_bundle()
        body = {"ik": _b64(pub["ik"]), "spk": _b64(pub["spk"]), "opk": _b64(pub["opk"])}
        requests.post(f"{self.server_url}/register/{self.username}", json=body, timeout=5)

    def _start_session(self, peer):
        response = requests.get(f"{self.server_url}/bundle/{peer}", timeout=5)
        raw = response.json()
        peer_bundle = {
            "ik": _unb64(raw["ik"]),
            "spk": _unb64(raw["spk"]),
            "opk": _unb64(raw["opk"]),
        }
        shared_key, ek_pub = x3dh_initiator(self.bundle.ik_priv, peer_bundle)
        ratchet = DoubleRatchet.init_alice(shared_key, peer_bundle["spk"])
        self.sessions[peer] = {"ratchet": ratchet, "first": True, "ek_pub": ek_pub}

    def send(self, peer, text, group=None):
        if peer not in self.sessions:
            self._start_session(peer)
        session = self.sessions[peer]
        header, ciphertext = session["ratchet"].encrypt(text.encode())
        envelope = {
            "sender": self.username,
            "dh_pub": _b64(header.dh_pub),
            "pn": header.pn,
            "n": header.n,
            "ciphertext": _b64(ciphertext),
        }
        if group is not None:
            envelope["group"] = group
        if session["first"]:
            envelope["ik_pub"] = _b64(self.bundle.ik_pub)
            envelope["ek_pub"] = _b64(session["ek_pub"])
            session["first"] = False
        requests.post(f"{self.server_url}/send/{peer}", json=envelope, timeout=5)

    def send_group(self, group, members, text):
        for member in members:
            if member != self.username:
                self.send(member, text, group=group)

    def receive(self):
        response = requests.get(f"{self.server_url}/messages/{self.username}", timeout=5)
        result = []
        for env in response.json():
            sender = env["sender"]
            if sender not in self.sessions:
                shared_key = x3dh_responder(self.bundle, _unb64(env["ik_pub"]), _unb64(env["ek_pub"]))
                ratchet = DoubleRatchet.init_bob(shared_key, (self.bundle.spk_priv, self.bundle.spk_pub))
                self.sessions[sender] = {"ratchet": ratchet, "first": False, "ek_pub": None}
            header = Header(_unb64(env["dh_pub"]), env["pn"], env["n"])
            plaintext = self.sessions[sender]["ratchet"].decrypt(header, _unb64(env["ciphertext"]))
            result.append((sender, plaintext.decode(), env.get("group")))
        return result