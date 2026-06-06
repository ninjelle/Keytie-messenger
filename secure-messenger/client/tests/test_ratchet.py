import pytest

import secure_core as sc
from ratchet import DoubleRatchet


def make_pair():
    shared_key = sc.kdf_sk(b"\x05" * 128)
    bob_keypair = sc.generate_keypair()
    alice = DoubleRatchet.init_alice(shared_key, bob_keypair[1])
    bob = DoubleRatchet.init_bob(shared_key, bob_keypair)
    return alice, bob


def test_single_message():
    alice, bob = make_pair()
    header, ciphertext = alice.encrypt(b"hi")
    assert bob.decrypt(header, ciphertext) == b"hi"


def test_multiple_messages_same_direction():
    alice, bob = make_pair()
    for text in [b"one", b"two", b"three"]:
        header, ciphertext = alice.encrypt(text)
        assert bob.decrypt(header, ciphertext) == text


def test_conversation_with_replies():
    alice, bob = make_pair()
    h1, c1 = alice.encrypt(b"hi bob")
    assert bob.decrypt(h1, c1) == b"hi bob"
    h2, c2 = bob.encrypt(b"hi alice")
    assert alice.decrypt(h2, c2) == b"hi alice"
    h3, c3 = alice.encrypt(b"how are you")
    assert bob.decrypt(h3, c3) == b"how are you"


def test_forward_secrecy():
    alice, bob = make_pair()

    h1, c1 = alice.encrypt(b"past secret")
    assert bob.decrypt(h1, c1) == b"past secret"

    h2, c2 = alice.encrypt(b"newer message")
    assert bob.decrypt(h2, c2) == b"newer message"

    leaked_ck = bob.ckr

    ck = leaked_ck
    for _ in range(10):
        ck, mk = sc.kdf_ck(ck)
        with pytest.raises(Exception):
            sc.decrypt(mk, c1, h1.to_bytes())