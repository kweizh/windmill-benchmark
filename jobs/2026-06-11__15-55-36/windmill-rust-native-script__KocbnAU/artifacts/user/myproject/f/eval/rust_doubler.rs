//! ```cargo
//! [dependencies]
//! serde_json = "1.0"
//! anyhow = "1"
//! ```

use serde_json::{json, Value};

fn main(name: String, threshold: i32) -> anyhow::Result<Value> {
    Ok(json!({
        "status": "ok",
        "computed": threshold * 2,
        "target": name
    }))
}
