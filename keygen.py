import base64
import socket
import platform

def obscure_secret():
    return [81, 98, 122, 51, 83, 102, 116, 113, 112, 111, 101, 84, 102, 100, 115, 102, 117]

def deobscure_secret(codes):
    return "".join(chr(c - 1) for c in codes)

def xor_encrypt_decrypt(data, key):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

def machine_fingerprint():
    return f"{socket.gethostname()}_{platform.node()}_{platform.machine()}"

def encode_key(machine_id):
    secret = deobscure_secret(obscure_secret())
    xored = xor_encrypt_decrypt(machine_id, secret)
    return base64.urlsafe_b64encode(xored.encode()).decode()

def generate_key():
    mf = machine_fingerprint()
    key = encode_key(mf)
    print(mf)
    print(key)

if __name__ == "__main__":
    generate_key()
