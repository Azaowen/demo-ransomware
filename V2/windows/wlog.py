import winreg as reg

key = r"Software\HEHEHE"
value_name = "RunStatus"

def check_log():
    try:
        with reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_READ) as registry_key:
            status, reg_type = reg.QueryValueEx(registry_key, value_name)
            return status
    except FileNotFoundError:
        return None

def update_log(status):
    try:
        with reg.CreateKey(reg.HKEY_CURRENT_USER, key) as registry_key:
            reg.SetValueEx(registry_key, value_name, 0, reg.REG_DWORD, status)
    except WindowsError as e:
        print(f"Error writing to registry: {e}")

