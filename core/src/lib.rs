/*
core/lib.rs
-----------
Entry point for the front end
*/

use pyo3::prelude::*;
use std::fs;

mod temp_storage;


#[pymodule]
fn keyplus_core(py: Python, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(temp_storage::temp_store_vault, py)?)?;
    m.add_function(wrap_pyfunction!(temp_storage::temp_load_vault, py)?)?;
    Ok(())
}