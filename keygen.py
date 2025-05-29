import base64
import socket
import platform

def xor_encrypt_decrypt(data, key):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

def machine_fingerprint():
    data = f"{socket.gethostname()}_{platform.node()}_{platform.machine()}"
    return data

def encode_key(machine_id, secret="Pay2RespondSecret"):
    xored = xor_encrypt_decrypt(machine_id, secret)
    return base64.urlsafe_b64encode(xored.encode()).decode()

def generate_key():
    mf = machine_fingerprint()
    key = encode_key(mf)
    print("Machine fingerprint:")
    print(mf)
    print("\nGenerated Key:")
    print(key)

if __name__ == "__main__":
    generate_key()
