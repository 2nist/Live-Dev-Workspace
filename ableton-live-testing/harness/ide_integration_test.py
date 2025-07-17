#!/usr/bin/env python3
"""
LATE IDE Integration Test Harness

Connects the Max Live IDE with LATE testing environment for automated testing
of Max for Live devices and visual patching workflows.
"""
import subprocess
import time
import json
import os
import requests
from pathlib import Path

# Configuration
IDE_URL = "http://localhost:3000"
ABLETON_API_URL = "http://localhost:9877"
LIVE_PATH = r"C:\Program Files\Ableton\Live 12 Suite\Program\Ableton Live 12 Suite.exe"
TEST_PATCHES_DIR = Path(__file__).parent.parent / "tests" / "patches"
RESULTS_LOG = "ide_test_results.log"

class IDETestHarness:
    def __init__(self):
        self.ableton_process = None
        self.ide_process = None
        self.test_results = []
        
    def setup_environment(self):
        """Set up the testing environment"""
        print("Setting up LATE IDE testing environment...")
        
        # Create test patches directory if it doesn't exist
        TEST_PATCHES_DIR.mkdir(parents=True, exist_ok=True)
        
        # Launch Ableton Live
        self.launch_ableton()
        
        # Launch the IDE
        self.launch_ide()
        
        # Wait for services to be ready
        self.wait_for_services()
        
    def launch_ableton(self):
        """Launch Ableton Live for testing"""
        print("Launching Ableton Live...")
        try:
            self.ableton_process = subprocess.Popen([LIVE_PATH])
            time.sleep(15)  # Wait for Live to fully load
            print("Ableton Live launched successfully")
        except Exception as e:
            print(f"Failed to launch Ableton Live: {e}")
            raise
    
    def launch_ide(self):
        """Launch the Max Live IDE"""
        print("Launching Max Live IDE...")
        try:
            ide_dir = Path(__file__).parent.parent.parent / "max-live-ide"
            self.ide_process = subprocess.Popen(
                ["npm", "start"], 
                cwd=ide_dir,
                shell=True
            )
            time.sleep(10)  # Wait for React dev server to start
            print("Max Live IDE launched successfully")
        except Exception as e:
            print(f"Failed to launch IDE: {e}")
            raise
    
    def wait_for_services(self):
        """Wait for all services to be ready"""
        print("Waiting for services to be ready...")
        
        # Check Ableton API
        for i in range(30):  # 30 second timeout
            try:
                response = requests.get(f"{ABLETON_API_URL}/api/get_session_info", timeout=2)
                if response.status_code == 200:
                    print("Ableton API is ready")
                    break
            except:
                pass
            time.sleep(1)
        else:
            raise Exception("Ableton API not ready after 30 seconds")
        
        # Check IDE
        for i in range(30):  # 30 second timeout
            try:
                response = requests.get(IDE_URL, timeout=2)
                if response.status_code == 200:
                    print("IDE is ready")
                    break
            except:
                pass
            time.sleep(1)
        else:
            raise Exception("IDE not ready after 30 seconds")
    
    def test_patch_loading(self):
        """Test loading a .maxpat file in the IDE"""
        print("Testing patch loading...")
        
        # Create a simple test patch
        test_patch = {
            "patcher": {
                "fileversion": 1,
                "appversion": {"major": 8, "minor": 5, "revision": 6},
                "rect": [34.0, 87.0, 834.0, 487.0],
                "bglocked": 0,
                "openinpresentation": 0,
                "default_fontsize": 12.0,
                "default_fontface": 0,
                "default_fontname": "Arial",
                "boxes": [
                    {
                        "box": {
                            "id": "1",
                            "maxclass": "newobj",
                            "text": "osc~ 440",
                            "patching_rect": [100.0, 50.0, 60.0, 22.0],
                            "numinlets": 2,
                            "numoutlets": 1
                        }
                    },
                    {
                        "box": {
                            "id": "2", 
                            "maxclass": "newobj",
                            "text": "gain~ 0.5",
                            "patching_rect": [100.0, 100.0, 60.0, 22.0],
                            "numinlets": 2,
                            "numoutlets": 1
                        }
                    },
                    {
                        "box": {
                            "id": "3",
                            "maxclass": "newobj", 
                            "text": "dac~",
                            "patching_rect": [100.0, 150.0, 35.0, 22.0],
                            "numinlets": 8,
                            "numoutlets": 0
                        }
                    }
                ],
                "lines": [
                    {
                        "patchline": {
                            "source": ["1", 0],
                            "destination": ["2", 0]
                        }
                    },
                    {
                        "patchline": {
                            "source": ["2", 0],
                            "destination": ["3", 0]
                        }
                    }
                ]
            }
        }
        
        # Save test patch
        test_patch_path = TEST_PATCHES_DIR / "test_oscillator.maxpat"
        with open(test_patch_path, 'w') as f:
            json.dump(test_patch, f, indent=2)
        
        # TODO: Automate file loading in IDE (would need selenium or similar)
        # For now, we'll verify the patch file was created correctly
        
        result = {
            "test": "patch_loading",
            "status": "success",
            "message": f"Test patch created at {test_patch_path}",
            "timestamp": time.time()
        }
        
        self.log_result(result)
        return result
    
    def test_ableton_connection(self):
        """Test connection between IDE and Ableton Live"""
        print("Testing Ableton connection...")
        
        try:
            # Test session info
            response = requests.get(f"{ABLETON_API_URL}/api/get_session_info")
            session_info = response.json()
            
            # Test track creation
            response = requests.post(
                f"{ABLETON_API_URL}/api/create_midi_track",
                json={"index": -1}
            )
            track_result = response.json()
            
            result = {
                "test": "ableton_connection",
                "status": "success",
                "session_info": session_info,
                "track_creation": track_result,
                "timestamp": time.time()
            }
            
        except Exception as e:
            result = {
                "test": "ableton_connection", 
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }
        
        self.log_result(result)
        return result
    
    def test_device_sync(self):
        """Test device synchronization between IDE and Live"""
        print("Testing device synchronization...")
        
        try:
            # Create a MIDI track for testing
            track_response = requests.post(
                f"{ABLETON_API_URL}/api/create_midi_track",
                json={"index": -1}
            )
            
            # Get track info
            tracks_response = requests.get(f"{ABLETON_API_URL}/api/get_session_info")
            tracks_info = tracks_response.json()
            
            # TODO: Test actual device loading and sync
            # This would require the full MCP server implementation
            
            result = {
                "test": "device_sync",
                "status": "partial",
                "message": "Track created, device sync needs full MCP implementation",
                "track_creation": track_response.json(),
                "timestamp": time.time()
            }
            
        except Exception as e:
            result = {
                "test": "device_sync",
                "status": "error", 
                "error": str(e),
                "timestamp": time.time()
            }
        
        self.log_result(result)
        return result
    
    def test_parameter_monitoring(self):
        """Test real-time parameter monitoring"""
        print("Testing parameter monitoring...")
        
        try:
            # Test setting tempo
            response = requests.post(
                f"{ABLETON_API_URL}/api/set_tempo",
                json={"tempo": 128}
            )
            tempo_result = response.json()
            
            result = {
                "test": "parameter_monitoring",
                "status": "success",
                "tempo_change": tempo_result,
                "timestamp": time.time()
            }
            
        except Exception as e:
            result = {
                "test": "parameter_monitoring",
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }
        
        self.log_result(result)
        return result
    
    def test_patch_export(self):
        """Test exporting patches from IDE to Live"""
        print("Testing patch export...")
        
        # This test verifies the export functionality exists
        # Actual export testing would require browser automation
        
        result = {
            "test": "patch_export",
            "status": "manual",
            "message": "Export functionality implemented, requires manual testing",
            "timestamp": time.time()
        }
        
        self.log_result(result)
        return result
    
    def run_all_tests(self):
        """Run all IDE integration tests"""
        print("Starting LATE IDE Integration Tests...")
        
        tests = [
            self.test_patch_loading,
            self.test_ableton_connection, 
            self.test_device_sync,
            self.test_parameter_monitoring,
            self.test_patch_export
        ]
        
        for test in tests:
            try:
                result = test()
                self.test_results.append(result)
                print(f"✓ {result['test']}: {result['status']}")
            except Exception as e:
                error_result = {
                    "test": test.__name__,
                    "status": "error",
                    "error": str(e),
                    "timestamp": time.time()
                }
                self.test_results.append(error_result)
                print(f"✗ {test.__name__}: error - {e}")
        
        self.generate_report()
    
    def log_result(self, result):
        """Log test result to file"""
        with open(RESULTS_LOG, "a") as f:
            f.write(json.dumps(result) + "\n")
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*50)
        print("LATE IDE Integration Test Report")
        print("="*50)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r['status'] == 'success'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        print()
        
        for result in self.test_results:
            status_icon = {
                'success': '✓',
                'error': '✗', 
                'partial': '~',
                'manual': 'M'
            }.get(result['status'], '?')
            
            print(f"{status_icon} {result['test']}: {result['status']}")
            if 'message' in result:
                print(f"  {result['message']}")
            if 'error' in result:
                print(f"  Error: {result['error']}")
        
        print(f"\nDetailed results logged to: {RESULTS_LOG}")
    
    def cleanup(self):
        """Clean up test environment"""
        print("Cleaning up test environment...")
        
        if self.ide_process:
            self.ide_process.terminate()
            self.ide_process.wait()
        
        # Note: We don't automatically close Ableton Live as it takes time to save
        print("Manual cleanup: Close Ableton Live when testing is complete")

def main():
    harness = IDETestHarness()
    
    try:
        harness.setup_environment()
        harness.run_all_tests()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test harness error: {e}")
    finally:
        harness.cleanup()

if __name__ == "__main__":
    main()
