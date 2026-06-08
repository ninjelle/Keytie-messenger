from x3dh import KeyBundle, x3dh_initiator, x3dh_responder
from ratchet import DoubleRatchet


def _establish(initiator, responder):
    responder_pub = responder.public_bundle()
    shared_init, ek_pub = x3dh_initiator(initiator.ik_priv, responder_pub)
    sender = DoubleRatchet.init_alice(shared_init, responder_pub["spk"])
    shared_resp = x3dh_responder(responder, initiator.ik_pub, ek_pub)
    receiver = DoubleRatchet.init_bob(shared_resp, (responder.spk_priv, responder.spk_pub))
    return sender, receiver


def test_group_message_delivered_to_every_member():
    alice = KeyBundle()
    bob = KeyBundle()
    carol = KeyBundle()

    to_bob, bob_session = _establish(alice, bob)
    to_carol, carol_session = _establish(alice, carol)

    message = "привет, группа".encode()

    header_b, ciphertext_b = to_bob.encrypt(message)
    header_c, ciphertext_c = to_carol.encrypt(message)

    assert bob_session.decrypt(header_b, ciphertext_b) == message
    assert carol_session.decrypt(header_c, ciphertext_c) == message


def test_group_message_encrypted_separately_per_member():
    alice = KeyBundle()
    bob = KeyBundle()
    carol = KeyBundle()

    to_bob, _ = _establish(alice, bob)
    to_carol, _ = _establish(alice, carol)

    message = "одинаковый текст".encode()

    _, ciphertext_b = to_bob.encrypt(message)
    _, ciphertext_c = to_carol.encrypt(message)

    assert ciphertext_b != ciphertext_c