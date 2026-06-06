import pytest

import secure_core as sc


def test_dh_symmetry():
    a_priv, a_pub = sc.generate_keypair()
    b_priv, b_pub = sc.generate_keypair()
    assert sc.dh(a_priv, b_pub) == sc.dh(b_priv, a_pub)


def test_dh_different_partners_differ():
    a_priv, a_pub = sc.generate_keypair()
    b_priv, b_pub = sc.generate_keypair()
    c_priv, c_pub = sc.generate_keypair()
    assert sc.dh(a_priv, b_pub) != sc.dh(a_priv, c_pub)


def test_kdf_ck_advances():
    ck0 = b"\x00" * 32
    ck1, mk1 = sc.kdf_ck(ck0)
    ck2, mk2 = sc.kdf_ck(ck1)
    assert mk1 != mk2
    assert ck1 != ck2
    assert len(mk1) == 32


def test_encrypt_decrypt_roundtrip():
    key = b"\x02" * 32
    ciphertext = sc.encrypt(key, b"hello", b"header")
    assert sc.decrypt(key, ciphertext, b"header") == b"hello"


def test_decrypt_fails_on_tampered_header():
    key = b"\x02" * 32
    ciphertext = sc.encrypt(key, b"hello", b"header")
    with pytest.raises(Exception):
        sc.decrypt(key, ciphertext, b"WRONG")


def test_invalid_key_length():
    with pytest.raises(Exception):
        sc.dh(b"short", b"\x00" * 32)