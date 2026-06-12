import os
import sys

def main():
    run_id = os.environ.get("ZEALT_RUN_ID")
    if not run_id:
        print("Error: ZEALT_RUN_ID environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Generating Windmill flow for run ID: {run_id}")
    
    # Path of the flow directory and flow.yaml
    flow_dir = f"/home/user/myproject/f/zealt/err_handler_{run_id}.flow"
    flow_yaml_path = f"{flow_dir}/flow.yaml"
    
    # Ensure directory exists
    os.makedirs(flow_dir, exist_ok=True)
    
    # YAML content with failure_module
    yaml_content = f"""summary: "Windmill Flow Error Handler - {run_id}"
description: "A Windmill flow with a custom error handler"
value:
  modules:
    - id: inner_script
      value:
        lock: ""
        type: rawscript
        content: |
          export async function main(should_fail: boolean) {{
            if (should_fail) {{
              throw new Error("Demanded failure from inner_script");
            }}
            return "Success";
          }}
        language: bun
        input_transforms:
          should_fail:
            type: javascript
            expr: flow_input.should_fail
  failure_module:
    id: failure
    value:
      lock: ""
      type: rawscript
      content: |
        export async function main(error: any) {{
          return {{
            "handled": true,
            "reason": error?.message || "Unknown error"
          }};
        }}
      language: bun
      input_transforms:
        error:
          type: javascript
          expr: error
schema:
  $schema: https://json-schema.org/draft/2020-12/schema
  type: object
  properties:
    should_fail:
      type: boolean
  required:
    - should_fail
"""
    
    with open(flow_yaml_path, "w") as f:
        f.write(yaml_content)
        
    print(f"Successfully wrote flow.yaml to {flow_yaml_path}")

if __name__ == "__main__":
    main()
