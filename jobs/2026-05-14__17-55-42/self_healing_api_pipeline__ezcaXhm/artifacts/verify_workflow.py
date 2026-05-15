"""
Simple verification script that checks the workflow structure without executing it.
"""

import ast
import sys


def verify_workflow_structure():
    """Verify the workflow file has the correct structure"""
    print("=" * 60)
    print("Verifying API Pipeline Workflow Structure")
    print("=" * 60)
    
    with open('/home/user/windmill-project/f/workflows/api_pipeline.py', 'r') as f:
        code = f.read()
    
    # Parse the code
    try:
        tree = ast.parse(code)
        print("✓ Python syntax is valid")
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False
    
    # Check for required imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)
    
    print(f"\nImports found: {imports}")
    
    required_imports = ['asyncio', 'json', 'urllib.request', 'urllib.error']
    for req in required_imports:
        if any(req in imp for imp in imports):
            print(f"✓ Found required import: {req}")
        else:
            print(f"✗ Missing required import: {req}")
            return False
    
    # Check for required functions
    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions[node.name] = node.args
    
    print(f"\nFunctions found: {list(functions.keys())}")
    
    # Check fetch_endpoint function
    if 'fetch_endpoint' not in functions:
        print("✗ Missing fetch_endpoint function")
        return False
    
    fetch_args = functions['fetch_endpoint']
    arg_names = [arg.arg for arg in fetch_args.args]
    print(f"fetch_endpoint args: {arg_names}")
    if 'endpoint' not in arg_names or 'max_retries' not in arg_names:
        print("✗ fetch_endpoint missing required args")
        return False
    print("✓ fetch_endpoint has correct signature")
    
    # Check main function
    if 'main' not in functions:
        print("✗ Missing main function")
        return False
    
    main_args = functions['main']
    arg_names = [arg.arg for arg in main_args.args]
    print(f"main args: {arg_names}")
    if 'endpoints' not in arg_names or 'max_retries' not in arg_names:
        print("✗ main missing required args")
        return False
    print("✓ main has correct signature")
    
    # Check for asyncio.sleep usage
    has_asyncio_sleep = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == 'sleep':
                    has_asyncio_sleep = True
    
    if has_asyncio_sleep:
        print("✓ Uses asyncio.sleep() for delays")
    else:
        print("✗ Missing asyncio.sleep() call")
        return False
    
    # Check for parallel usage
    has_parallel = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id == 'parallel':
                    has_parallel = True
    
    if has_parallel:
        print("✓ Uses parallel() function")
    else:
        print("✗ Missing parallel() call")
        return False
    
    # Check for urllib.request usage
    has_urllib = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == 'urlopen':
                    has_urllib = True
    
    if has_urllib:
        print("✓ Uses urllib.request.urlopen()")
    else:
        print("✗ Missing urllib.request.urlopen() call")
        return False
    
    # Check for JSON writing
    has_json_dump = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == 'dump':
                    has_json_dump = True
    
    if has_json_dump:
        print("✓ Uses json.dump() for writing report")
    else:
        print("✗ Missing json.dump() call")
        return False
    
    # Check for health report structure
    report_path = '/home/user/windmill-project/pipeline_report.json'
    if report_path in code:
        print(f"✓ Writes report to correct path: {report_path}")
    else:
        print(f"✗ Report path not found in code")
        return False
    
    # Check for required health report fields
    required_fields = ['total', 'successful', 'failed', 'success_rate']
    all_present = all(field in code for field in required_fields)
    if all_present:
        print(f"✓ Health report contains all required fields: {required_fields}")
    else:
        print(f"✗ Health report missing required fields")
        return False
    
    # Check for exponential backoff pattern (2 ** attempt)
    if '2 **' in code or '2**' in code:
        print("✓ Implements exponential backoff (2 ** attempt)")
    else:
        print("✗ Missing exponential backoff pattern")
        return False
    
    print("\n" + "=" * 60)
    print("All structure checks passed! ✓")
    print("=" * 60)
    return True


def check_code_logic():
    """Check the code logic by analyzing the source"""
    print("\n" + "=" * 60)
    print("Analyzing Code Logic")
    print("=" * 60)
    
    with open('/home/user/windmill-project/f/workflows/api_pipeline.py', 'r') as f:
        code = f.read()
    
    # Check retry logic
    if 'for attempt in range(max_retries):' in code:
        print("✓ Has retry loop")
    else:
        print("✗ Missing retry loop")
        return False
    
    # Check for success/failure return values
    if "'status': 'success'" in code and "'status': 'failed'" in code:
        print("✓ Returns success/failed status")
    else:
        print("✗ Missing status return values")
        return False
    
    # Check for concurrency parameter
    if 'concurrency=3' in code:
        print("✓ Uses concurrency=3")
    else:
        print("✗ Missing concurrency parameter")
        return False
    
    # Check for result counting
    if "result['status'] == 'success'" in code:
        print("✓ Counts successful results")
    else:
        print("✗ Missing result counting")
        return False
    
    print("\n" + "=" * 60)
    print("All logic checks passed! ✓")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = verify_workflow_structure() and check_code_logic()
    sys.exit(0 if success else 1)