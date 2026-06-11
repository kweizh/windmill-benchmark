//! ```cargo
//! [dependencies]
//! serde_json = "1.0"
//! anyhow = "1.0"
//! ```

use serde_json::json;

pub fn main(name: String, threshold: i32) -> anyhow::Result<serde_json::Value> {
    Ok(json!({
        "status": "ok",
        "computed": threshold * 2,
        "target": name
    }))
}