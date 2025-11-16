#!/usr/bin/env python3
"""
APK Modifier for Dragon Land
Modifies PhotonServerSettings to point to new server
"""

import os
import sys
import yaml
import shutil
import subprocess
from pathlib import Path

class APKModifier:
    def __init__(self, apk_path, output_dir="/workspace/dragon-land-server/modified-apk"):
        self.apk_path = apk_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.work_dir = self.output_dir / "work"
        self.work_dir.mkdir(exist_ok=True)
        
    def decompile_apk(self):
        """Decompile APK using apktool"""
        print("[1] Decompiling APK...")
        decompile_dir = self.work_dir / "decompiled"
        
        # Check if apktool is available
        if not shutil.which("apktool"):
            print("⚠ apktool not found, extracting as ZIP...")
            # Fallback: extract as ZIP
            import zipfile
            with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                zip_ref.extractall(decompile_dir)
            print("✓ APK extracted as ZIP")
        else:
            # Use apktool for proper decompilation
            cmd = ["apktool", "d", "-f", self.apk_path, "-o", str(decompile_dir)]
            subprocess.run(cmd, check=True)
            print("✓ APK decompiled successfully")
        
        return decompile_dir
    
    def modify_photon_settings(self, decompile_dir, new_appid=None, new_server=None, new_port=5055):
        """Modify PhotonServerSettings.asset"""
        print("[2] Modifying Photon settings...")
        
        # Find PhotonServerSettings
        settings_path = None
        for root, dirs, files in os.walk(decompile_dir):
            if "PhotonServerSettings.asset" in files:
                settings_path = Path(root) / "PhotonServerSettings.asset"
                break
        
        if not settings_path:
            print("⚠ PhotonServerSettings.asset not found!")
            return False
        
        print(f"   Found: {settings_path}")
        
        # Read current settings
        with open(settings_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except:
            print("⚠ Could not parse as YAML, using text replacement...")
            data = None
        
        if data:
            # Modify using YAML structure
            if new_appid:
                data['MonoBehaviour']['AppID'] = new_appid
            if new_server:
                data['MonoBehaviour']['HostType'] = 2  # SelfHosted
                data['MonoBehaviour']['ServerAddress'] = new_server
                data['MonoBehaviour']['ServerPort'] = new_port
            
            # Write back
            with open(settings_path, 'w') as f:
                yaml.dump(data, f)
        else:
            # Fallback: text replacement
            if new_appid:
                old_appid = "1eb3a592-f2d1-41c1-ac3a-cd6308fca5cb"
                content = content.replace(old_appid, new_appid)
            
            if new_server:
                # Change HostType to SelfHosted
                content = content.replace("HostType: 4", "HostType: 2")
                content = content.replace("ServerAddress:", f"ServerAddress: {new_server}")
                content = content.replace("ServerPort: 5055", f"ServerPort: {new_port}")
            
            with open(settings_path, 'w') as f:
                f.write(content)
        
        print("✓ Photon settings modified")
        return True
    
    def rebuild_apk(self, decompile_dir):
        """Rebuild APK"""
        print("[3] Rebuilding APK...")
        output_apk = self.output_dir / "DragonLand_Modified.apk"
        
        if shutil.which("apktool"):
            cmd = ["apktool", "b", str(decompile_dir), "-o", str(output_apk)]
            subprocess.run(cmd, check=True)
        else:
            # Fallback: rezip
            import zipfile
            with zipfile.ZipFile(output_apk, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(decompile_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(decompile_dir)
                        zipf.write(file_path, arcname)
        
        print(f"✓ APK rebuilt: {output_apk}")
        return output_apk
    
    def sign_apk(self, apk_path):
        """Sign APK with debug keystore"""
        print("[4] Signing APK...")
        signed_apk = self.output_dir / "DragonLand_Modified_Signed.apk"
        
        # Create debug keystore if it doesn't exist
        keystore = self.work_dir / "debug.keystore"
        if not keystore.exists():
            cmd = [
                "keytool", "-genkeypair", "-v",
                "-keystore", str(keystore),
                "-storepass", "android",
                "-alias", "androiddebugkey",
                "-keypass", "android",
                "-keyalg", "RSA",
                "-keysize", "2048",
                "-validity", "10000",
                "-dname", "CN=Android Debug,O=Android,C=US"
            ]
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                print("   ✓ Debug keystore created")
            except:
                print("   ⚠ Could not create keystore (keytool not available)")
                return apk_path
        
        # Sign APK
        try:
            # Try using jarsigner
            cmd = [
                "jarsigner", "-verbose",
                "-keystore", str(keystore),
                "-storepass", "android",
                "-keypass", "android",
                "-signedjar", str(signed_apk),
                str(apk_path),
                "androiddebugkey"
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✓ APK signed: {signed_apk}")
            return signed_apk
        except:
            print("   ⚠ Could not sign APK (jarsigner not available)")
            return apk_path
    
    def modify(self, new_appid=None, new_server=None, new_port=5055):
        """Complete modification workflow"""
        print("="*60)
        print("DRAGON LAND APK MODIFIER")
        print("="*60)
        print(f"Input APK: {self.apk_path}")
        print(f"Output Directory: {self.output_dir}")
        if new_appid:
            print(f"New Photon AppID: {new_appid}")
        if new_server:
            print(f"New Server: {new_server}:{new_port}")
        print("="*60)
        
        try:
            # Decompile
            decompile_dir = self.decompile_apk()
            
            # Modify
            if not self.modify_photon_settings(decompile_dir, new_appid, new_server, new_port):
                print("❌ Failed to modify settings")
                return None
            
            # Rebuild
            rebuilt_apk = self.rebuild_apk(decompile_dir)
            
            # Sign
            final_apk = self.sign_apk(rebuilt_apk)
            
            print("\n" + "="*60)
            print("✓ MODIFICATION COMPLETE!")
            print("="*60)
            print(f"Modified APK: {final_apk}")
            print(f"Size: {final_apk.stat().st_size / (1024*1024):.2f} MB")
            print("\nNext steps:")
            print("1. Upload to Appetize.io")
            print("2. Test connection to server")
            print("3. Verify gameplay")
            print("="*60)
            
            return final_apk
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    # Configuration
    apk_path = "/workspace/full thang/Dragon Land (1).apk"
    
    # Example configurations:
    
    # Option 1: Use new Photon Cloud AppID (recommended)
    # Get from: https://dashboard.photonengine.com
    new_photon_appid = "YOUR_NEW_PHOTON_APPID_HERE"
    
    # Option 2: Use custom server (Codespaces)
    # codespaces_url = "https://your-codespace-5055.app.github.dev"
    
    print("Dragon Land APK Modification Tool")
    print("-" * 60)
    print("\nSelect modification type:")
    print("1. Change Photon AppID only (use new Photon Cloud)")
    print("2. Point to custom server (Codespaces)")
    print("3. Both (AppID + Custom Server)")
    print("4. Extract only (no modification)")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    modifier = APKModifier(apk_path)
    
    if choice == "1":
        appid = input("Enter new Photon AppID: ").strip()
        modifier.modify(new_appid=appid)
    elif choice == "2":
        server = input("Enter server address: ").strip()
        port = input("Enter port (default 5055): ").strip() or "5055"
        modifier.modify(new_server=server, new_port=int(port))
    elif choice == "3":
        appid = input("Enter new Photon AppID: ").strip()
        server = input("Enter server address: ").strip()
        port = input("Enter port (default 5055): ").strip() or "5055"
        modifier.modify(new_appid=appid, new_server=server, new_port=int(port))
    elif choice == "4":
        decompile_dir = modifier.decompile_apk()
        print(f"\n✓ APK extracted to: {decompile_dir}")
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    # Check if running with arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--auto":
            # Auto mode: just extract
            apk_path = "/workspace/full thang/Dragon Land (1).apk"
            modifier = APKModifier(apk_path)
            decompile_dir = modifier.decompile_apk()
            print(f"\n✓ APK decompiled to: {decompile_dir}")
    else:
        main()
