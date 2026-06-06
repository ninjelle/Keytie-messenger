use pyo3::prelude::*;
use pyo3::types::PyBytes;
use pyo3::exceptions::PyValueError;
use x25519_dalek::{StaticSecret, PublicKey};
use hmac::{Hmac, Mac};
use sha2::Sha256;
use hkdf::Hkdf;
use chacha20poly1305::{ChaCha20Poly1305, Key, Nonce};
use chacha20poly1305::aead::{Aead, KeyInit, Payload};

type HmacSha256 = Hmac<Sha256>;

fn to_key(bytes: &[u8]) -> PyResult<[u8; 32]> {
    bytes
        .try_into()
        .map_err(|_| PyValueError::new_err("ключ должен быть длиной ровно 32 байта"))
}

#[pyfunction]
fn generate_keypair(py: Python<'_>) -> (Bound<'_, PyBytes>, Bound<'_, PyBytes>) {
    let secret = StaticSecret::random();
    let public = PublicKey::from(&secret);
    (
        PyBytes::new(py, &secret.to_bytes()),
        PyBytes::new(py, public.as_bytes()),
    )
}

#[pyfunction]
fn dh<'py>(py: Python<'py>, private_key: &[u8], their_public: &[u8]) -> PyResult<Bound<'py, PyBytes>> {
    let secret = StaticSecret::from(to_key(private_key)?);
    let public = PublicKey::from(to_key(their_public)?);
    let shared = secret.diffie_hellman(&public);
    Ok(PyBytes::new(py, shared.as_bytes()))
}

#[pyfunction]
fn kdf_ck<'py>(py: Python<'py>, chain_key: &[u8]) -> PyResult<(Bound<'py, PyBytes>, Bound<'py, PyBytes>)> {
    let mut mac_mk = <HmacSha256 as Mac>::new_from_slice(chain_key)
        .map_err(|_| PyValueError::new_err("неверная длина ключа цепочки"))?;
    mac_mk.update(&[0x01]);
    let message_key = mac_mk.finalize().into_bytes();

    let mut mac_ck = <HmacSha256 as Mac>::new_from_slice(chain_key)
        .map_err(|_| PyValueError::new_err("неверная длина ключа цепочки"))?;
    mac_ck.update(&[0x02]);
    let next_chain_key = mac_ck.finalize().into_bytes();

    Ok((
        PyBytes::new(py, next_chain_key.as_slice()),
        PyBytes::new(py, message_key.as_slice()),
    ))
}

#[pyfunction]
fn kdf_rk<'py>(py: Python<'py>, root_key: &[u8], dh_output: &[u8]) -> PyResult<(Bound<'py, PyBytes>, Bound<'py, PyBytes>)> {
    let hk = Hkdf::<Sha256>::new(Some(root_key), dh_output);
    let mut okm = [0u8; 64];
    hk.expand(b"DoubleRatchet", &mut okm)
        .map_err(|_| PyValueError::new_err("ошибка HKDF"))?;
    Ok((
        PyBytes::new(py, &okm[..32]),
        PyBytes::new(py, &okm[32..]),
    ))
}

#[pyfunction]
fn encrypt<'py>(py: Python<'py>, message_key: &[u8], plaintext: &[u8], associated_data: &[u8]) -> PyResult<Bound<'py, PyBytes>> {
    let key_arr = to_key(message_key)?;
    let cipher = ChaCha20Poly1305::new(Key::from_slice(&key_arr));
    let nonce = Nonce::from_slice(&[0u8; 12]);
    let payload = Payload { msg: plaintext, aad: associated_data };
    let ciphertext = cipher
        .encrypt(nonce, payload)
        .map_err(|_| PyValueError::new_err("ошибка шифрования"))?;
    Ok(PyBytes::new(py, &ciphertext))
}

#[pyfunction]
fn decrypt<'py>(py: Python<'py>, message_key: &[u8], ciphertext: &[u8], associated_data: &[u8]) -> PyResult<Bound<'py, PyBytes>> {
    let key_arr = to_key(message_key)?;
    let cipher = ChaCha20Poly1305::new(Key::from_slice(&key_arr));
    let nonce = Nonce::from_slice(&[0u8; 12]);
    let payload = Payload { msg: ciphertext, aad: associated_data };
    let plaintext = cipher
        .decrypt(nonce, payload)
        .map_err(|_| PyValueError::new_err("расшифровка не удалась: подмена данных или неверный ключ"))?;
    Ok(PyBytes::new(py, &plaintext))
}

#[pyfunction]
fn kdf_sk<'py>(py: Python<'py>, key_material: &[u8]) -> PyResult<Bound<'py, PyBytes>> {
    let salt = [0u8; 32];
    let hk = Hkdf::<Sha256>::new(Some(&salt), key_material);
    let mut okm = [0u8; 32];
    hk.expand(b"X3DH", &mut okm)
        .map_err(|_| PyValueError::new_err("ошибка HKDF"))?;
    Ok(PyBytes::new(py, &okm))
}

#[pymodule]
fn secure_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(generate_keypair, m)?)?;
    m.add_function(wrap_pyfunction!(dh, m)?)?;
    m.add_function(wrap_pyfunction!(kdf_ck, m)?)?;
    m.add_function(wrap_pyfunction!(kdf_rk, m)?)?;
    m.add_function(wrap_pyfunction!(encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(decrypt, m)?)?;
    m.add_function(wrap_pyfunction!(kdf_sk, m)?)?;
    Ok(())
}