//! ```cargo
//! [dependencies]
//! serde_json = "1.0"
//! anyhow = "1.0"
//! ```

pub fn main(name: String, threshold: i32) -> anyhow::Result<serde_json::Value> {
    Ok(serde_json::json!({
        "status": "ok",
        "computed": threshold * 2,
        "target": name
    }))
}
