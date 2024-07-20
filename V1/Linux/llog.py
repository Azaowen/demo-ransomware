import os

config_file = os.path.expanduser("~/.config/hehe.conf")

def check_log():
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            status = f.read().strip()
            return status
    return None

def update_log(status):
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, "w") as f:
        f.write(str(status))
