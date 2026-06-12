# Windmill: Run a Script Inside an Arbitrary Docker Image

## Background
Windmill is a code-first developer platform that can run any container image directly from a script. The supported mechanism on Windmill Cloud (`https://app.windmill.dev`) is the **sandboxed image runtime**: a Bash script is annotated with `# sandbox <image>` and the body of that script then runs **inside the referenced image**, sandboxed by [nsjail](https://www.windmill.dev/docs/advanced/security_isolation). The runtime is daemonless (no Docker socket, no DinD), so it works on Windmill Cloud out-of-the-box. The other annotation, the bare `# docker` form, is a legacy daemon-based runtime that requires a mounted Docker socket and only works on self-hosted setups; do NOT use it for this task.

Docker scripts are stored on disk as a pair of files (a script content file plus a `.script.yaml` metadata file), and the canonical Windmill *language identifier* for these scripts is the Bash language — the worker dispatches the body to the image's `/bin/sh -c`. Reference: [Run Docker containers](https://www.windmill.dev/docs/advanced/docker) and the [Docker quickstart](https://www.windmill.dev/docs/getting_started/scripts_quickstart/docker).

Your job is to author and deploy such a sandboxed Docker script to the Windmill Cloud workspace, then trigger it and persist the result so the verifier can confirm the script actually executed on a cloud worker, inside the requested container image.

## Requirements
- Read the current `run-id` from the `ZEALT_RUN_ID` environment variable. Compute `SAFE_ID = ZEALT_RUN_ID.replace('-', '_')` and use it to namespace every Windmill path you create, so concurrent runs do not collide.
- Author a single Windmill **sandboxed Docker script** at the Windmill workspace path `f/docker_${SAFE_ID}/hello_alpine`. On disk this corresponds to a file pair under the project root:
  - A script content file paired with a sibling `<path>.script.yaml` metadata file.
  - The `.script.yaml` metadata must declare the script using the **exact language identifier that Windmill stores for sandboxed Docker scripts** — this is the language Windmill uses to dispatch the body via `/bin/sh -c` (see the Docker quickstart docs). Do NOT invent a language string.
  - The script body must start with the `# sandbox <image>` annotation that selects an `alpine:3` lightweight base image (you may also write `alpine:3.X` for an explicit minor, but stay on the Alpine 3 series). The legacy bare `# docker` annotation is NOT acceptable — it requires a self-hosted Docker socket and will not execute on Windmill Cloud.
- The script must accept exactly one positional Windmill argument named `message` of type `string`. Inside the body, parameters bind positionally as `$1`, `$2`, … (this is how Windmill bridges typed arguments into the image's shell).
- When executed, the script must print to stdout a single final line of the form:

  ```
  hello <message> from <NAME>
  ```

  where `<message>` is the argument value and `<NAME>` is the value of the `NAME` field from `/etc/os-release` inside the running container (for `alpine:3`, `/etc/os-release` yields `NAME="Alpine Linux"`, so this line must contain `Alpine Linux`). Per the Windmill docs, the **last line** of stdout is what is captured as the script's string result.
- Deploy the script to the cloud workspace using the `wmill` CLI (e.g. via `wmill sync push --yes` against the configured workspace, or `wmill script push`). Authentication uses the API token in `WINDMILL_TOKEN`, the workspace id in `WINDMILL_WORKSPACE`, and the base URL `https://app.windmill.dev`. **NEVER start a local Windmill instance.**
- After deployment, exercise the script remotely with `message = "harbor-${ZEALT_RUN_ID}"` (using the raw `ZEALT_RUN_ID`, hyphens preserved). Capture the returned result and write a log file with the produced result and the deployed script path (see Acceptance Criteria for the exact format).

## Implementation Hints
- The `# sandbox <image>` runtime is daemonless and is explicitly documented as **available on Windmill Cloud**. You do NOT need a self-hosted worker, a special worker tag, or any Docker socket — see https://www.windmill.dev/docs/advanced/docker.
- The supported language enum for Windmill scripts does NOT include `docker` — the `wmill` CLI and Windmill API use the Bash language identifier (the script body is run with `/bin/sh -c` inside the chosen image). Inspect the Docker quickstart and the [local development table](https://www.windmill.dev/docs/advanced/local_development) for the exact language string Windmill expects.
- Windmill's positional argument convention for shell scripts is `x="$1"` (and `dflt="${2:-default}"` for optional ones). The argument name on the left side of the `=` becomes the typed Windmill parameter; you must use a binding named `message`.
- Alpine's `/etc/os-release` file exposes `NAME="Alpine Linux"`. You can extract it with a shell one-liner such as `. /etc/os-release && echo "hello $1 from $NAME"` to ensure the final stdout line matches the required format.
- To deploy declaratively, bootstrap a `wmill.yaml` (`wmill init`), register the cloud workspace (`wmill workspace add ... --token "$WINDMILL_TOKEN" https://app.windmill.dev/`), then run `wmill sync push --yes`. Alternatively, push the single script with `wmill script push <file>`.
- To run the deployed script and capture its result without ambient logs, use the synchronous run endpoint:
  `POST https://app.windmill.dev/api/w/${WINDMILL_WORKSPACE}/jobs/run_wait_result/p/f/docker_${SAFE_ID}/hello_alpine` with `Authorization: Bearer ${WINDMILL_TOKEN}` and JSON body `{"message": "harbor-${ZEALT_RUN_ID}"}`. The response body is the script's result (a JSON string, with the last stdout line as its value).
- The first invocation may take a little longer on a fresh worker because Windmill needs to pull and flatten the image rootfs (it then caches it by digest). Allow generous time, but do NOT add any latency assertions to your solution.

## Acceptance Criteria
- Project path: /home/user/myproject
- Ensure the deployment AND a real remote execution are performed against `https://app.windmill.dev`; the artifacts below must exist on disk.
- Log file: /home/user/myproject/output.log
- File pair on disk (using `SAFE_ID = ZEALT_RUN_ID.replace('-', '_')`):
  - A Windmill script content file at `/home/user/myproject/f/docker_${SAFE_ID}/hello_alpine.<ext>`, where `<ext>` is the extension Windmill uses for a sandboxed Docker script (i.e. the file extension that maps to the language identifier declared in the metadata file). The verifier will look up both common candidates.
  - A sibling metadata file at `/home/user/myproject/f/docker_${SAFE_ID}/hello_alpine.script.yaml`. This file MUST declare the script's `language` as the **exact identifier Windmill uses for sandboxed Docker scripts** (not the string `docker`).
- The script content file MUST contain a `# sandbox <image>` annotation referencing an `alpine:3` (or `alpine:3.X`) base image. The legacy bare `# docker` annotation is NOT acceptable.
- The script content file MUST declare a typed Windmill argument named `message` (e.g. via `message="$1"` at the top of the body, since Windmill infers shell-script parameters from positional `$1`, `$2`, … bindings).
- The script MUST be deployed to the cloud workspace identified by `WINDMILL_WORKSPACE` at the path `f/docker_${SAFE_ID}/hello_alpine` and MUST be retrievable via the Windmill scripts API (`GET /api/w/${WINDMILL_WORKSPACE}/scripts/get/p/f/docker_${SAFE_ID}/hello_alpine` must return HTTP 200 and the response JSON's `language` field MUST equal the same identifier declared in the local `.script.yaml`).
- When the deployed script is executed with input `{"message": "harbor-${ZEALT_RUN_ID}"}` via the synchronous `run_wait_result` endpoint, the response body (the JSON-decoded result, which is a string captured from the last line of stdout) MUST equal `hello harbor-${ZEALT_RUN_ID} from Alpine Linux` (with `${ZEALT_RUN_ID}` substituted by the actual run-id).
- The log file must contain the following two lines exactly (substituting `${ZEALT_RUN_ID}` with the actual run-id):
  - `Script path: f/docker_${SAFE_ID}/hello_alpine`
  - `Result: hello harbor-${ZEALT_RUN_ID} from Alpine Linux`

