import subprocess

def test_speed():
    try:
        result = subprocess.run(
            ["speedtest-cli", "--simple"],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return "Failed to test internet speed."