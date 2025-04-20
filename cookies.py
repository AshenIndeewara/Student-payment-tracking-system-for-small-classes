import base64


def encrypt_text(text):
    """
    Encrypts text using XOR encryption and encodes the result in Base64 (numbers and letters only).
    :param text: The plain text to encrypt (string)
    :param key: The encryption key (string)
    :return: Encrypted text (Base64 string)
    """
    # XOR encryption
    
    key = "dfsdf4235423JGK"
    encrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text))
    # Encode the encrypted text in Base64
    encrypted_base64 = base64.b64encode(encrypted.encode()).decode()
    return encrypted_base64

def decrypt_text(encrypted_text):
    """
    Decrypts Base64-encoded XOR-encrypted text.
    :param encrypted_text: The Base64-encoded encrypted text (string)
    :param key: The encryption key (string)
    :return: Decrypted plain text (string)
    """
    # Decode the Base64 string
    key = "dfsdf4235423JGK"
    encrypted = base64.b64decode(encrypted_text).decode()
    # XOR decryption
    decrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(encrypted))
    return decrypted
