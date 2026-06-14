def encrypt(plaintext, key):
    """
    Encrypts plaintext using the Caesar Cipher with a numeric shift key.
    Returns a tuple: (ciphertext, steps)
    - steps is a list of dictionaries detailing the transformation of each character.
    """
    try:
        shift = int(key) % 26
    except ValueError:
        raise ValueError("Caesar cipher key must be an integer.")

    ciphertext = []
    steps = []

    for char in plaintext:
        if char.isalpha():
            start_code = ord('A') if char.isupper() else ord('a')
            orig_pos = ord(char) - start_code
            new_pos = (orig_pos + shift) % 26
            new_char = chr(start_code + new_pos)
            ciphertext.append(new_char)
            steps.append({
                'char': char,
                'op': f"({orig_pos} + {shift}) % 26 = {new_pos}",
                'result': new_char
            })
        else:
            ciphertext.append(char)
            steps.append({
                'char': char,
                'op': "Non-alphabetic, remains unchanged",
                'result': char
            })

    return "".join(ciphertext), steps

def decrypt(ciphertext, key):
    """
    Decrypts ciphertext using the Caesar Cipher with a numeric shift key.
    Returns a tuple: (plaintext, steps)
    """
    try:
        shift = int(key) % 26
    except ValueError:
        raise ValueError("Caesar cipher key must be an integer.")

    plaintext = []
    steps = []

    for char in ciphertext:
        if char.isalpha():
            start_code = ord('A') if char.isupper() else ord('a')
            orig_pos = ord(char) - start_code
            new_pos = (orig_pos - shift) % 26
            new_char = chr(start_code + new_pos)
            plaintext.append(new_char)
            steps.append({
                'char': char,
                'op': f"({orig_pos} - {shift}) % 26 = {new_pos}",
                'result': new_char
            })
        else:
            plaintext.append(char)
            steps.append({
                'char': char,
                'op': "Non-alphabetic, remains unchanged",
                'result': char
            })

    return "".join(plaintext), steps
