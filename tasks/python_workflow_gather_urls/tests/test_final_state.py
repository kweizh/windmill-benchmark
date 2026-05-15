import os
import ast

TARGET = "/home/user/windmill-project/f/workflows/url_monitor.py"


# ── helpers ────────────────────────────────────────────────────────────────────

def _read_source() -> str:
    with open(TARGET, "r", encoding="utf-8") as fh:
        return fh.read()


def _parse_tree(source: str) -> ast.Module:
    return ast.parse(source)


def _decorator_names(node) -> list:
    """Return the flat name(s) of each decorator on an async/sync def node."""
    names = []
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name):
            names.append(dec.id)
        elif isinstance(dec, ast.Attribute):
            names.append(dec.attr)
        elif isinstance(dec, ast.Call):
            func = dec.func
            if isinstance(func, ast.Name):
                names.append(func.id)
            elif isinstance(func, ast.Attribute):
                names.append(func.attr)
    return names


def _function_nodes(tree: ast.Module) -> dict:
    """Return a mapping of function name → AST node for top-level functions."""
    return {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


# ── tests ──────────────────────────────────────────────────────────────────────

def test_file_exists():
    """The workflow file must exist at the required path."""
    assert os.path.isfile(TARGET), f"File not found: {TARGET}"


def test_imports_workflow_and_task_from_wmill():
    """The file must import `workflow` and `task` from `wmill`."""
    source = _read_source()
    tree = _parse_tree(source)

    imported_names: set = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "wmill":
            for alias in node.names:
                imported_names.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "wmill":
                    # covers `import wmill` followed by `wmill.task` usage
                    imported_names.add("wmill")

    assert "task" in imported_names or "wmill" in imported_names, (
        "`task` (or the `wmill` module) must be imported from `wmill`."
    )
    assert "workflow" in imported_names or "wmill" in imported_names, (
        "`workflow` (or the `wmill` module) must be imported from `wmill`."
    )


def test_task_decorator_used_at_least_twice():
    """@task must decorate at least two functions (check_url and aggregate)."""
    source = _read_source()
    tree = _parse_tree(source)

    task_decorated = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and "task" in _decorator_names(node)
    ]
    assert len(task_decorated) >= 2, (
        f"Expected at least 2 functions decorated with @task, "
        f"found {len(task_decorated)}."
    )


def test_workflow_decorator_used():
    """@workflow must decorate at least one function (main)."""
    source = _read_source()
    tree = _parse_tree(source)

    workflow_decorated = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and "workflow" in _decorator_names(node)
    ]
    assert len(workflow_decorated) >= 1, (
        "Expected at least 1 function decorated with @workflow."
    )


def test_asyncio_gather_used():
    """The workflow must use asyncio.gather for parallel URL fetching."""
    source = _read_source()
    assert "asyncio.gather" in source, (
        "`asyncio.gather` must be used in the workflow for parallel execution."
    )


def test_check_url_has_error_fallback():
    """check_url must contain a try/except that returns status 0 on failure."""
    source = _read_source()
    tree = _parse_tree(source)
    funcs = _function_nodes(tree)

    assert "check_url" in funcs, "`check_url` function not found."

    func_node = funcs["check_url"]

    # Walk the function body looking for a Try node
    try_nodes = [n for n in ast.walk(func_node) if isinstance(n, ast.Try)]
    assert try_nodes, "`check_url` must contain a try/except block."

    # The source of the function body must reference status 0 / 'status': 0
    func_source = ast.get_source_segment(source, func_node) or ""
    assert "'status': 0" in func_source or '"status": 0' in func_source, (
        "`check_url` except clause must return `{'url': url, 'status': 0, 'ok': False}`."
    )


def test_aggregate_function_exists():
    """An `aggregate` function must be defined."""
    source = _read_source()
    tree = _parse_tree(source)
    funcs = _function_nodes(tree)
    assert "aggregate" in funcs, "`aggregate` function not found."


def test_aggregate_returns_required_keys():
    """aggregate must reference total, successful, and failed in its body."""
    source = _read_source()
    tree = _parse_tree(source)
    funcs = _function_nodes(tree)

    assert "aggregate" in funcs, "`aggregate` function not found."
    agg_source = ast.get_source_segment(source, funcs["aggregate"]) or ""

    for key in ("total", "successful", "failed"):
        assert key in agg_source, (
            f"`aggregate` function body must reference the key `{key}`."
        )
