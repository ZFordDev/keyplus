// core/temp_storage.rs

use pyo3::prelude::*;
use std::fs;
use std::path::Path;

#[pyfunction]
pub fn temp_store_vault(path: &str, json_blob: &str) -> PyResult<()> {
    let parent = Path::new(path).parent().unwrap();
    fs::create_dir_all(parent)?;
    fs::write(path, json_blob)?;
    Ok(())
}

#[pyfunction]
pub fn temp_load_vault(path: &str) -> PyResult<String> {
    if !Path::new(path).exists() {
        return Ok("{\"entries\": []}".to_string());
    }
    let data = fs::read_to_string(path)?;
    Ok(data)
}
