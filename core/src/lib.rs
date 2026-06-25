"""
core/lib.rs
-----------

Entry point for the front end
"""

use pyo3::prelude::*;
use std::fs;

#[pyfunction]
fn store_vault(path: &str, json_blob: &str) -> PyResult<()> {
    fs::write(path, json_blob)?;
    Ok(())
}

#[pyfunction]
fn load_vault(path: &str) -> PyResult<String> {
    let data = fs::read_to_string(path)?;
    Ok(data)
}

#[pymodule]
fn keyplus_core(py: Python, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(store_vault, py)?)?;
    m.add_function(wrap_pyfunction!(load_vault, py)?)?;
    Ok(())
}
