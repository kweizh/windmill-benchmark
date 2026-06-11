//! ```cargo
//! [dependencies]
//! serde_json = "1.0"
//! anyhow = "1.0"
//! ```

use anyhow::Result;
use serde_json::{json, Value};

fn main(name: String, threshold: i32) -> Result<Value> {
    Ok(json!({
        "status": "ok",
        "computed": threshold * 2,
        "target": name
    }))
}
