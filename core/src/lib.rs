use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

#[pyfunction]
fn version() -> &'static str {
    "0.1.0"
}

#[pyfunction]
fn pack_nibbles(values: Vec<u8>) -> PyResult<Vec<u8>> {
    for &value in &values {
        if value > 0x0F {
            return Err(PyValueError::new_err("nibble value must be <= 15"));
        }
    }

    let mut out = Vec::with_capacity((values.len() + 1) / 2);
    let mut i = 0;
    while i < values.len() {
        let hi = values[i] << 4;
        let lo = if i + 1 < values.len() { values[i + 1] } else { 0 };
        out.push(hi | lo);
        i += 2;
    }
    Ok(out)
}

#[pyfunction]
fn unpack_nibbles(data: Vec<u8>, value_count: usize) -> Vec<u8> {
    let mut out = Vec::with_capacity(value_count);
    for byte in data {
        if out.len() < value_count {
            out.push((byte >> 4) & 0x0F);
        }
        if out.len() < value_count {
            out.push(byte & 0x0F);
        }
        if out.len() >= value_count {
            break;
        }
    }
    out
}

#[pyfunction]
fn find_subsequence(haystack: Vec<u8>, needle: Vec<u8>) -> PyResult<Vec<usize>> {
    if needle.is_empty() {
        return Err(PyValueError::new_err("needle must not be empty"));
    }

    if needle.len() > haystack.len() {
        return Ok(Vec::new());
    }

    let mut matches = Vec::new();
    let end = haystack.len() - needle.len();
    for i in 0..=end {
        if haystack[i..i + needle.len()] == needle[..] {
            matches.push(i);
        }
    }
    Ok(matches)
}

#[pyfunction]
fn fnv1a64(data: Vec<u8>) -> u64 {
    const OFFSET: u64 = 0xcbf29ce484222325;
    const PRIME: u64 = 0x100000001b3;

    let mut hash = OFFSET;
    for b in data {
        hash ^= b as u64;
        hash = hash.wrapping_mul(PRIME);
    }
    hash
}

#[pymodule]
fn zpe_finance_rs(_py: Python, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(version, module)?)?;
    module.add_function(wrap_pyfunction!(pack_nibbles, module)?)?;
    module.add_function(wrap_pyfunction!(unpack_nibbles, module)?)?;
    module.add_function(wrap_pyfunction!(find_subsequence, module)?)?;
    module.add_function(wrap_pyfunction!(fnv1a64, module)?)?;
    Ok(())
}
