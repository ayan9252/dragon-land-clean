#!/usr/bin/env python3
"""
Dragon Land - Complete Automation Script
Handles server deployment, APK modification, and Appetize.io testing
"""

import os
import sys
import time
import requests
import json
from pathlib import Path

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Set via environment variable
APPETIZE_API_KEY = None  # User needs to provide this

class DeploymentAutomation:
    def __init__(self):
        self.base_path = Path("/workspace/dragon-land-server")
        self.apk_path = Path("/workspace/full thang/Dragon Land (1).apk")
        self.analysis_file = Path("/workspace/DRAGON_LAND_ANALYSIS.md")
        
    def step1_verify_environment(self):
        """Verify all required files and tools"""
        print("\n" + "="*70)
        print("STEP 1: ENVIRONMENT VERIFICATION")
        print("="*70)
        
        checks = {
            "APK File": self.apk_path.exists(),
            "Analysis Report": self.analysis_file.exists(),
            "Server Directory": self.base_path.exists(),
            "Backend API": (self.base_path / "backend-api/app.py").exists(),
            "APK Tools": (self.base_path / "apk-tools/modify_apk.py").exists(),
        }
        
        all_passed = True
        for name, passed in checks.items():
            status = "✓" if passed else "❌"
            print(f"  {status} {name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n✓ All checks passed!")
        else:
            print("\n❌ Some checks failed. Please review.")
            return False
        
        return True
    
    def step2_start_backend_server(self):
        """Start the FastAPI backend server"""
        print("\n" + "="*70)
        print("STEP 2: STARTING BACKEND SERVER")
        print("="*70)
        
        # Start server in background
        import subprocess
        import signal
        
        server_script = self.base_path / "backend-api/app.py"
        
        print("Starting FastAPI server...")
        print("  URL: http://localhost:8000")
        print("  Docs: http://localhost:8000/docs")
        
        # Create start script
        start_script = f"""
import sys
sys.path.insert(0, '{self.base_path / "backend-api"}')
from app import app
import uvicorn

uvicorn.run(app, host="0.0.0.0", port=8000)
"""
        
        script_file = self.base_path / "start_server.py"
        with open(script_file, 'w') as f:
            f.write(start_script)
        
        # Start in background
        proc = subprocess.Popen(
            [sys.executable, str(script_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"  Process ID: {proc.pid}")
        print("  Waiting for server to start...")
        time.sleep(3)
        
        # Test connection
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✓ Backend server is running!")
                print(f"  Response: {response.json()}")
                return proc
            else:
                print("❌ Server started but not responding correctly")
                return None
        except Exception as e:
            print(f"❌ Could not connect to server: {e}")
            return None
    
    def step3_photon_configuration(self):
        """Guide user through Photon setup"""
        print("\n" + "="*70)
        print("STEP 3: PHOTON SERVER CONFIGURATION")
        print("="*70)
        
        print("\nPhoton Setup Options:")
        print("\n  Option A: Photon Cloud (Recommended)")
        print("  -----------------------------------------")
        print("  1. Visit: https://dashboard.photonengine.com")
        print("  2. Create free account")
        print("  3. Create new 'Photon PUN' application")
        print("  4. Copy the AppID")
        print("\n  Original AppID: 1eb3a592-f2d1-41c1-ac3a-cd6308fca5cb")
        
        print("\n  Option B: Self-Hosted (Advanced)")
        print("  -----------------------------------------")
        print("  1. Download Photon Server SDK")
        print("  2. Configure PhotonServer.config")
        print("  3. Deploy to Codespaces")
        print("  4. Expose port 5055 or WebSocket 9090")
        
        choice = input("\nWhich option? (A/B or skip): ").strip().upper()
        
        if choice == "A":
            appid = input("Enter your new Photon AppID: ").strip()
            return {"type": "cloud", "appid": appid}
        elif choice == "B":
            server = input("Enter server address: ").strip()
            port = input("Enter port (default 5055): ").strip() or "5055"
            return {"type": "selfhosted", "server": server, "port": int(port)}
        else:
            print("⚠ Skipping Photon configuration")
            return None
    
    def step4_modify_apk(self, photon_config):
        """Modify APK with new server settings"""
        print("\n" + "="*70)
        print("STEP 4: APK MODIFICATION")
        print("="*70)
        
        if not photon_config:
            print("⚠ No Photon configuration provided, skipping APK modification")
            return None
        
        # Import the modifier
        sys.path.insert(0, str(self.base_path / "apk-tools"))
        from modify_apk import APKModifier
        
        modifier = APKModifier(str(self.apk_path))
        
        if photon_config["type"] == "cloud":
            modified_apk = modifier.modify(new_appid=photon_config["appid"])
        else:
            modified_apk = modifier.modify(
                new_server=photon_config["server"],
                new_port=photon_config["port"]
            )
        
        return modified_apk
    
    def step5_appetize_upload(self, apk_path):
        """Upload to Appetize.io and test"""
        print("\n" + "="*70)
        print("STEP 5: APPETIZE.IO TESTING")
        print("="*70)
        
        if not APPETIZE_API_KEY:
            print("\n⚠ No Appetize.io API key configured")
            print("\nManual Upload Steps:")
            print("  1. Visit: https://appetize.io/upload")
            print("  2. Upload APK: " + str(apk_path))
            print("  3. Test in browser")
            print("\nFor API automation, set APPETIZE_API_KEY")
            return None
        
        print("Uploading to Appetize.io...")
        
        try:
            with open(apk_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    "https://api.appetize.io/v1/apps",
                    auth=(APPETIZE_API_KEY, ''),
                    files=files,
                    data={'platform': 'android'}
                )
            
            if response.status_code == 200:
                result = response.json()
                public_key = result['publicKey']
                app_url = f"https://appetize.io/app/{public_key}"
                
                print(f"✓ Upload successful!")
                print(f"  Public Key: {public_key}")
                print(f"  App URL: {app_url}")
                print("\nTest the app by visiting the URL above")
                
                return {
                    "public_key": public_key,
                    "url": app_url
                }
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"❌ Error uploading: {e}")
            return None
    
    def step6_testing_checklist(self):
        """Interactive testing checklist"""
        print("\n" + "="*70)
        print("STEP 6: TESTING CHECKLIST")
        print("="*70)
        
        tests = [
            "APK loads without crashes",
            "Connects to server (check logs)",
            "Player authentication works",
            "Main menu displays correctly",
            "Can start a level",
            "Dragon movement responds",
            "Multiplayer lobby accessible (if applicable)",
            "No network timeout errors",
            "Game saves progress",
            "Performance is acceptable"
        ]
        
        print("\nPerform these tests on Appetize.io:\n")
        results = {}
        
        for i, test in enumerate(tests, 1):
            print(f"{i}. {test}")
            result = input("   Pass? (y/n/skip): ").strip().lower()
            results[test] = result
        
        # Summary
        passed = sum(1 for r in results.values() if r == 'y')
        failed = sum(1 for r in results.values() if r == 'n')
        skipped = sum(1 for r in results.values() if r not in ['y', 'n'])
        
        print("\n" + "-"*70)
        print(f"Test Results: {passed} passed, {failed} failed, {skipped} skipped")
        
        if failed == 0 and passed > 0:
            print("✓ All tests passed!")
        elif failed > 0:
            print("⚠ Some tests failed. Review logs and configuration.")
        
        return results
    
    def generate_report(self, server_proc, photon_config, modified_apk, appetize_result, test_results):
        """Generate final deployment report"""
        print("\n" + "="*70)
        print("DEPLOYMENT REPORT")
        print("="*70)
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "backend_server": {
                "status": "running" if server_proc else "not started",
                "url": "http://localhost:8000",
                "docs": "http://localhost:8000/docs"
            },
            "photon": photon_config or {"status": "not configured"},
            "apk": {
                "original": str(self.apk_path),
                "modified": str(modified_apk) if modified_apk else "not modified",
                "size_mb": modified_apk.stat().st_size / (1024*1024) if modified_apk else 0
            },
            "appetize": appetize_result or {"status": "not uploaded"},
            "tests": test_results or {}
        }
        
        report_file = self.base_path / "deployment_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✓ Report saved to: {report_file}")
        
        # Print summary
        print("\nDEPLOYMENT SUMMARY")
        print("-"*70)
        
        if server_proc:
            print(f"✓ Backend Server: Running (PID {server_proc.pid})")
        
        if photon_config:
            print(f"✓ Photon: Configured ({photon_config['type']})")
        
        if modified_apk:
            print(f"✓ Modified APK: {modified_apk}")
        
        if appetize_result:
            print(f"✓ Appetize.io: {appetize_result['url']}")
        
        print("\nNext Steps:")
        print("  1. Test the app on Appetize.io")
        print("  2. Monitor server logs")
        print("  3. Verify network traffic")
        print("  4. Check for errors")
        
        return report_file
    
    def run(self):
        """Execute complete automation workflow"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║          DRAGON LAND SERVER - COMPLETE AUTOMATION               ║
║                                                                  ║
║  This script will:                                              ║
║  1. Verify environment                                          ║
║  2. Start backend server                                        ║
║  3. Configure Photon networking                                 ║
║  4. Modify APK                                                  ║
║  5. Upload to Appetize.io                                       ║
║  6. Run testing checklist                                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")
        
        input("Press Enter to begin...")
        
        # Step 1: Verify
        if not self.step1_verify_environment():
            print("\n❌ Environment verification failed. Exiting.")
            return
        
        # Step 2: Start server
        server_proc = self.step2_start_backend_server()
        
        # Step 3: Photon config
        photon_config = self.step3_photon_configuration()
        
        # Step 4: Modify APK
        modified_apk = self.step4_modify_apk(photon_config)
        
        # Step 5: Appetize
        apk_to_test = modified_apk if modified_apk else self.apk_path
        appetize_result = self.step5_appetize_upload(apk_to_test)
        
        # Step 6: Testing
        test_results = self.step6_testing_checklist()
        
        # Generate report
        report_file = self.generate_report(
            server_proc,
            photon_config,
            modified_apk,
            appetize_result,
            test_results
        )
        
        print("\n" + "="*70)
        print("✓ AUTOMATION COMPLETE!")
        print("="*70)
        print(f"\nFull report: {report_file}")
        print("\nServer is running. To stop:")
        if server_proc:
            print(f"  kill {server_proc.pid}")

if __name__ == "__main__":
    automation = DeploymentAutomation()
    automation.run()
