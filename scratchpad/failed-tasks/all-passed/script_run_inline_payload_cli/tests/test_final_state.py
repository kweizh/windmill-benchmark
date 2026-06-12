import json
import os

RESULT_PATH = "/home/user/result.json"

# The pre-deployed Windmill script `f/zealt_eval/add_numbers` returns the sum of
# its two integer inputs. For inputs a=17 and b=25 (specified in the task), the
# expected JSON result is the integer 42.
EXPECTED_RESULT = 42


def test_result_file_exists():
    assert os.path.isfile(RESULT_PATH), (
        f"Expected the output file {RESULT_PATH} to exist after the task is "
        "completed, but it was not found. The agent must invoke "
        "`wmill script run f/zealt_eval/add_numbers ...` and redirect its JSON "
        f"result into {RESULT_PATH}."
    )


def test_result_file_contains_valid_json():
    # The file should be parseable as JSON. We intentionally do not assert on
    # raw text formatting, ANSI colors, or surrounding CLI log lines; we only
    # check the parsed JSON value.
    with open(RESULT_PATH, "r", encoding="utf-8") as f:
        raw = f.read()
    try:
        json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"The contents of {RESULT_PATH} could not be parsed as JSON. "
            "Make sure to capture the silent/clean JSON output of "
            "`wmill script run` (which excludes streamed logs) into the file. "
            f"Parse error: {exc}. Raw content: {raw!r}"
        )


def test_result_value_matches_expected_sum():
    with open(RESULT_PATH, "r", encoding="utf-8") as f:
        parsed = json.load(f)
    assert parsed == EXPECTED_RESULT, (
        f"Expected the JSON value in {RESULT_PATH} to equal {EXPECTED_RESULT} "
        "(the result returned by the pre-deployed Windmill script "
        "`f/zealt_eval/add_numbers` for inputs a=17, b=25), but got "
        f"{parsed!r}."
    )
