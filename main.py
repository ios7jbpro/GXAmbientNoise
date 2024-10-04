import platform
import subprocess

def detect_os_and_run():
    current_os = platform.system()

    if current_os == "Windows":
        print("Detected OS: Windows")
        subprocess.run(["python", "main_windows.py"])
    elif current_os == "Linux":
        print("Detected OS: Linux")
        subprocess.run(["python3", "main_linux.py"])
    else:
        print(f"Unsupported OS: {current_os}")

if __name__ == "__main__":
    detect_os_and_run()

