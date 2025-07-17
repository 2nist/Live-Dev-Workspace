#!/usr/bin/env python3
"""
LATE IDE Quick Test Runner

Quick automated tests for IDE functionality without launching full Ableton Live.
Uses the mock server for fast feedback during development.
"""
import subprocess
import time
import requests
import json
from pathlib import Path

MOCK_SERVER_URL = "http://localhost:9877"
IDE_URL = "http://localhost:3000"

class QuickIDETest:
    def __init__(self):
        self.mock_process = None
        self.test_results = []
        
    def start_mock_server(self):
        """Start the LATE mock server"""
        print("Starting LATE mock server...")
        mock_server_path = Path(__file__).parent.parent / "mock" / "mock_server.py"
        self.mock_process = subprocess.Popen(["python", str(mock_server_path)])
        time.sleep(3)  # Wait for server to start
        
        # Verify mock server is running
        try:
            response = requests.get(f"{MOCK_SERVER_URL}/api/get_session_info")
            print("✓ Mock server started successfully")
            return True
        except:
            print("✗ Failed to start mock server")
            return False
    
    def test_api_endpoints(self):
        """Test all mock API endpoints"""
        print("Testing mock API endpoints...")
        
        endpoints = [
            ("GET", "/api/get_session_info", None),
            ("POST", "/api/create_midi_track", {"index": -1}),
            ("POST", "/api/set_tempo", {"tempo": 120}),
        ]
        
        results = []
        for method, endpoint, data in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{MOCK_SERVER_URL}{endpoint}")
                else:
                    response = requests.post(f"{MOCK_SERVER_URL}{endpoint}", json=data)
                
                result = {
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": response.status_code,
                    "response": response.json(),
                    "success": response.status_code == 200
                }
                results.append(result)
                status = "✓" if result["success"] else "✗"
                print(f"  {status} {method} {endpoint}: {response.status_code}")
                
            except Exception as e:
                result = {
                    "endpoint": endpoint,
                    "method": method,
                    "error": str(e),
                    "success": False
                }
                results.append(result)
                print(f"  ✗ {method} {endpoint}: Error - {e}")
        
        return results
    
    def test_patch_validation(self):
        """Test patch loading and validation"""
        print("Testing patch validation...")
        
        # Load test patch
        test_patch_path = Path(__file__).parent.parent / "tests" / "patches" / "test_oscillator_device.json"
        
        try:
            with open(test_patch_path, 'r') as f:
                patch_data = json.load(f)
            
            # Validate patch structure
            required_fields = ['patcher']
            patcher_fields = ['boxes', 'lines']
            
            validation_results = []
            
            # Check top-level structure
            for field in required_fields:
                if field in patch_data:
                    validation_results.append(f"✓ {field} field present")
                else:
                    validation_results.append(f"✗ {field} field missing")
            
            # Check patcher structure
            if 'patcher' in patch_data:
                for field in patcher_fields:
                    if field in patch_data['patcher']:
                        validation_results.append(f"✓ patcher.{field} present")
                    else:
                        validation_results.append(f"✗ patcher.{field} missing")
            
            # Check boxes and lines counts
            boxes = patch_data.get('patcher', {}).get('boxes', [])
            lines = patch_data.get('patcher', {}).get('lines', [])
            
            validation_results.append(f"✓ Found {len(boxes)} objects")
            validation_results.append(f"✓ Found {len(lines)} connections")
            
            print("  Patch validation results:")
            for result in validation_results:
                print(f"    {result}")
            
            return {
                "test": "patch_validation",
                "status": "success",
                "patch_file": str(test_patch_path),
                "validation_results": validation_results
            }
            
        except Exception as e:
            print(f"  ✗ Patch validation failed: {e}")
            return {
                "test": "patch_validation",
                "status": "error",
                "error": str(e)
            }
    
    def test_ide_responsiveness(self):
        """Test if IDE is responsive (if running)"""
        print("Testing IDE responsiveness...")
        
        try:
            response = requests.get(IDE_URL, timeout=5)
            if response.status_code == 200:
                print("  ✓ IDE is responsive")
                return {
                    "test": "ide_responsiveness", 
                    "status": "success",
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                print(f"  ✗ IDE returned status {response.status_code}")
                return {
                    "test": "ide_responsiveness",
                    "status": "error", 
                    "status_code": response.status_code
                }
        except Exception as e:
            print(f"  ~ IDE not running or not accessible: {e}")
            return {
                "test": "ide_responsiveness",
                "status": "skipped",
                "reason": "IDE not running"
            }
    
    def run_quick_tests(self):
        """Run all quick tests"""
        print("Starting LATE IDE Quick Tests...\n")
        
        # Start mock server
        if not self.start_mock_server():
            print("Cannot continue without mock server")
            return
        
        # Run tests
        tests = [
            ("API Endpoints", self.test_api_endpoints),
            ("Patch Validation", self.test_patch_validation),
            ("IDE Responsiveness", self.test_ide_responsiveness)
        ]
        
        all_results = []
        
        for test_name, test_func in tests:
            print(f"\n{test_name}:")
            try:
                result = test_func()
                all_results.append(result)
            except Exception as e:
                print(f"  ✗ Test failed with exception: {e}")
                all_results.append({
                    "test": test_name,
                    "status": "error",
                    "error": str(e)
                })
        
        # Generate summary
        print(f"\n{'='*50}")
        print("LATE IDE Quick Test Summary")
        print(f"{'='*50}")
        
        success_count = 0
        total_count = 0
        
        for result in all_results:
            if isinstance(result, list):  # API endpoints return list
                for item in result:
                    total_count += 1
                    if item.get('success', False):
                        success_count += 1
            else:
                total_count += 1
                if result.get('status') == 'success':
                    success_count += 1
        
        print(f"Tests completed: {total_count}")
        print(f"Successful: {success_count}")
        print(f"Success rate: {(success_count/total_count)*100:.1f}%")
        
        # Save results
        results_file = "quick_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\nDetailed results saved to: {results_file}")
        
        return all_results
    
    def cleanup(self):
        """Clean up test environment"""
        if self.mock_process:
            print("\nStopping mock server...")
            self.mock_process.terminate()
            self.mock_process.wait()

def main():
    tester = QuickIDETest()
    
    try:
        tester.run_quick_tests()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test runner error: {e}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()
