from flask import Flask
from Crypto.PublicKey import RSA

app = Flask(__name__)

@app.route('/key', methods=['GET'])
def generate_key():
    # Tạo cặp khóa RSA (2048 bit)
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    # Echo private key ra màn hình
    print(private_key)

    # Trả về public key dưới dạng chuỗi
    return public_key, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
