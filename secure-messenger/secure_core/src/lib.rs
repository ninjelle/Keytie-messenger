use pyo3::prelude::*;

/// Простая проверка, что Rust-ядро собралось и доступно из Python.
/// На Дне 2 здесь появятся настоящие криптофункции (DH, KDF, шифрование).
#[pyfunction]
fn hello() -> PyResult<String> {
    Ok("Привет из Rust-ядра! Криптография на подходе.".to_string())
}

/// Модуль Python. Имя функции должно совпадать с [lib].name в Cargo.toml.
#[pymodule]
fn secure_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello, m)?)?;
    Ok(())
}
