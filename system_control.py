import os
import subprocess
import platform
import json

class SystemControl:
    @staticmethod
    def get_system_stats():
        """Returns laptop hardware & system status summary"""
        try:
            os_name = f"{platform.system()} {platform.release()}"
            processor = platform.processor() or "AMD / Intel Processor"
            return {
                "os": os_name,
                "processor": processor,
                "status": "Online & Operational",
                "admin_access": "Granted via Backend Server"
            }
        except Exception as e:
            return {"os": "Windows 11", "status": f"Error: {str(e)}"}

    @staticmethod
    def launch_application(app_name):
        """Launches a desktop application on Windows laptop"""
        app_lower = app_name.lower().strip()
        
        try:
            if "notepad" in app_lower:
                subprocess.Popen(["notepad.exe"])
                return f"💻 Launching **Notepad** on your laptop!"
            elif "calculator" in app_lower or "calc" in app_lower:
                subprocess.Popen(["calc.exe"])
                return f"💻 Opening **Calculator** on your laptop!"
            elif "cmd" in app_lower or "terminal" in app_lower or "command prompt" in app_lower:
                subprocess.Popen(["cmd.exe", "/c", "start", "cmd"])
                return f"💻 Opening **Command Prompt Terminal** on your laptop!"
            elif "chrome" in app_lower or "browser" in app_lower:
                subprocess.Popen(["cmd.exe", "/c", "start", "chrome"])
                return f"💻 Opening **Web Browser** on your laptop!"
            elif "explorer" in app_lower or "file manager" in app_lower or "folder" in app_lower:
                subprocess.Popen(["explorer.exe"])
                return f"💻 Opening **File Explorer** on your laptop!"
            else:
                # General Windows start command
                subprocess.Popen(["cmd.exe", "/c", "start", app_lower], shell=True)
                return f"💻 Attempting to launch application **\"{app_name.capitalize()}\"** on your laptop!"
        except Exception as e:
            return f"⚠️ Could not launch {app_name}: {str(e)}"
