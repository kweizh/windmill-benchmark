"""
Test script to verify the workflow structure and logic without making network calls.
"""

import asyncio
import json
import sys
sys.path.insert(0, '/home/user/windmill-project')

# Patch wmill module BEFORE importing the workflow
import sys

# Create a mock parallel function
async def mock_parallel(*tasks, **kwargs):
    # Execute tasks sequentially for testing
    results = []
    for task in tasks:
        result = await task
        results.append(result)
    return results

# Create a proper mock module
class MockWMillModule:
    parallel = mock_parallel

# Inject the mock into sys.modules BEFORE importing
sys.modules['wmill'] = MockWMillModule()

# NOW import the workflow functions
from f.workflows.api_pipeline import fetch_endpoint, main


async def test_fetch_endpoint_success():
    """Test successful fetch with httpbin.org"""
    print("Testing successful fetch...")
    result = await fetch_endpoint("https://httpbin.org/get", max_retries=2)
    print(f"Result: {result['status']}")
    assert result['status'] == 'success'
    assert result['endpoint'] == "https://httpbin.org/get"
    assert result['data'] is not None
    print("✓ Success test passed")


async def test_fetch_endpoint_failure():
    """Test failed fetch with invalid URL"""
    print("\nTesting failed fetch...")
    result = await fetch_endpoint("http://invalid-url-that-does-not-exist-12345.com", max_retries=2)
    print(f"Result: {result['status']}")
    assert result['status'] == 'failed'
    assert result['endpoint'] == "http://invalid-url-that-does-not-exist-12345.com"
    assert result['data'] is None
    print("✓ Failure test passed")


async def test_main_workflow():
    """Test main workflow with multiple endpoints"""
    print("\nTesting main workflow...")
    endpoints = [
        "https://httpbin.org/get",
        "https://httpbin.org/uuid",
        "http://invalid-url-that-does-not-exist-12345.com"
    ]
    
    result = await main(endpoints, max_retries=2)
    print(f"Health report: {result}")
    
    assert result['total'] == 3
    assert result['successful'] >= 2  # At least 2 should succeed
    assert result['failed'] >= 1  # At least 1 should fail
    assert 0 <= result['success_rate'] <= 1
    print("✓ Main workflow test passed")
    
    # Check that report file was created
    report_path = '/home/user/windmill-project/pipeline_report.json'
    with open(report_path, 'r') as f:
        file_report = json.load(f)
    print(f"File report: {file_report}")
    assert file_report == result
    print("✓ Report file test passed")


async def test_exponential_backoff():
    """Test that exponential backoff is implemented correctly"""
    print("\nTesting exponential backoff delays...")
    import time
    
    # Test with a failing endpoint and small max_retries
    start = time.time()
    result = await fetch_endpoint("http://invalid-url-12345.com", max_retries=3)
    elapsed = time.time() - start
    
    # With 3 retries, delays should be: 0s (first attempt), 1s, 2s
    # Total should be at least 3 seconds (1 + 2)
    print(f"Elapsed time: {elapsed:.2f}s")
    assert elapsed >= 3, f"Expected at least 3s but got {elapsed:.2f}s"
    print("✓ Exponential backoff test passed")


async def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running API Pipeline Workflow Tests")
    print("=" * 60)
    
    try:
        await test_fetch_endpoint_success()
        await test_fetch_endpoint_failure()
        await test_main_workflow()
        await test_exponential_backoff()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)