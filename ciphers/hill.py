import re
import math

def egcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = egcd(b % a, a)
        return g, x - (b // a) * y, y

def mod_inverse(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        return None  # modular inverse does not exist
    else:
        return x % m

def parse_key(key_str):
    """
    Parses key_str into a 2x2 integer matrix.
    Accepts either a 4-letter word or 4 comma-separated integers.
    """
    key_str = key_str.strip()
    
    # Check if it's a 4-letter word
    word_match = re.match(r'^[A-Za-z]{4}$', key_str)
    if word_match:
        vals = [ord(c.upper()) - ord('A') for c in key_str]
    else:
        # Try to parse as 4 comma-separated integers
        parts = re.split(r'[,\s]+', key_str)
        parts = [p for p in parts if p]
        if len(parts) == 4:
            try:
                vals = [int(p) for p in parts]
            except ValueError:
                raise ValueError("Key must be a 4-letter word or 4 comma-separated integers.")
        else:
            raise ValueError("Key must be a 4-letter word or exactly 4 integers (e.g. 7,8,11,11).")
            
    # Form 2x2 matrix
    matrix = [
        [vals[0], vals[1]],
        [vals[2], vals[3]]
    ]
    return matrix

def validate_matrix(matrix):
    """
    Validates if the 2x2 matrix is invertible modulo 26.
    Returns determinant, mod_inverse of determinant, or raises ValueError.
    """
    a = matrix[0][0]
    b = matrix[0][1]
    c = matrix[1][0]
    d = matrix[1][1]
    
    det = (a * d - b * c) % 26
    det_inv = mod_inverse(det, 26)
    
    if det_inv is None:
        raise ValueError(
            f"Matrix [[{a},{b}],[{c},{d}]] is not valid for Hill Cipher. "
            f"Determinant is {det}, which has no modular inverse modulo 26 "
            f"(gcd({det}, 26) = {math.gcd(det, 26)} != 1). Please choose another key."
        )
        
    return det, det_inv

def encrypt(plaintext, key_str):
    """
    Encrypts plaintext using Hill Cipher 2x2 matrix.
    Returns (ciphertext, steps)
    """
    matrix = parse_key(key_str)
    det, det_inv = validate_matrix(matrix)
    
    # Filter text to uppercase A-Z
    text_clean = re.sub(r'[^A-Z]', '', plaintext.upper())
    if not text_clean:
        raise ValueError("Plaintext must contain at least one alphabetic character.")
        
    # Pad text with 'X' if length is odd
    original_len = len(text_clean)
    if len(text_clean) % 2 != 0:
        text_clean += 'X'
        
    ciphertext_chars = []
    steps = []
    
    steps.append({
        'type': 'info',
        'message': f"Key Matrix: [[{matrix[0][0]}, {matrix[0][1]}], [{matrix[1][0]}, {matrix[1][1]}]]\n"
                   f"Determinant: {det}, Determinant Inverse mod 26: {det_inv}"
    })
    
    for i in range(0, len(text_clean), 2):
        char1 = text_clean[i]
        char2 = text_clean[i+1]
        
        v1 = ord(char1) - ord('A')
        v2 = ord(char2) - ord('A')
        
        # Matrix multiplication
        # [ c1 ]   [ a  b ] [ v1 ]
        # [ c2 ] = [ c  d ] [ v2 ]
        c1 = (matrix[0][0] * v1 + matrix[0][1] * v2) % 26
        c2 = (matrix[1][0] * v1 + matrix[1][1] * v2) % 26
        
        nc1 = chr(c1 + ord('A'))
        nc2 = chr(c2 + ord('A'))
        
        ciphertext_chars.append(nc1)
        ciphertext_chars.append(nc2)
        
        steps.append({
            'type': 'vector',
            'input': f"[{char1}={v1}, {char2}={v2}]",
            'calculation': f"[{matrix[0][0]}*{v1} + {matrix[0][1]}*{v2}] % 26 = {c1} ({nc1})\n"
                           f"[{matrix[1][0]}*{v1} + {matrix[1][1]}*{v2}] % 26 = {c2} ({nc2})",
            'output': f"{nc1}{nc2}"
        })
        
    return "".join(ciphertext_chars), steps

def decrypt(ciphertext, key_str):
    """
    Decrypts ciphertext using Hill Cipher 2x2 matrix.
    Returns (plaintext, steps)
    """
    matrix = parse_key(key_str)
    det, det_inv = validate_matrix(matrix)
    
    # Clean ciphertext
    ciphertext_clean = re.sub(r'[^A-Z]', '', ciphertext.upper())
    if not ciphertext_clean:
        raise ValueError("Ciphertext must contain at least one alphabetic character.")
    if len(ciphertext_clean) % 2 != 0:
        raise ValueError("Hill Cipher ciphertext must have an even length.")
        
    # Calculate inverse matrix
    # K_inv = det_inv * adj(K) mod 26
    # adj(K) = [[d, -b], [-c, a]]
    a, b = matrix[0][0], matrix[0][1]
    c, d = matrix[1][0], matrix[1][1]
    
    inv_matrix = [
        [(d * det_inv) % 26, ((-b) * det_inv) % 26],
        [((-c) * det_inv) % 26, (a * det_inv) % 26]
    ]
    
    plaintext_chars = []
    steps = []
    
    steps.append({
        'type': 'info',
        'message': f"Key Matrix: [[{a}, {b}], [{c}, {d}]]\n"
                   f"Determinant: {det}, Inverse Det: {det_inv}\n"
                   f"Inverse Matrix: [[{inv_matrix[0][0]}, {inv_matrix[0][1]}], [{inv_matrix[1][0]}, {inv_matrix[1][1]}]]"
    })
    
    for i in range(0, len(ciphertext_clean), 2):
        char1 = ciphertext_clean[i]
        char2 = ciphertext_clean[i+1]
        
        v1 = ord(char1) - ord('A')
        v2 = ord(char2) - ord('A')
        
        # Matrix multiplication with Inverse Matrix
        p1 = (inv_matrix[0][0] * v1 + inv_matrix[0][1] * v2) % 26
        p2 = (inv_matrix[1][0] * v1 + inv_matrix[1][1] * v2) % 26
        
        nc1 = chr(p1 + ord('A'))
        nc2 = chr(p2 + ord('A'))
        
        plaintext_chars.append(nc1)
        plaintext_chars.append(nc2)
        
        steps.append({
            'type': 'vector',
            'input': f"[{char1}={v1}, {char2}={v2}]",
            'calculation': f"[{inv_matrix[0][0]}*{v1} + {inv_matrix[0][1]}*{v2}] % 26 = {p1} ({nc1})\n"
                           f"[{inv_matrix[1][0]}*{v1} + {inv_matrix[1][1]}*{v2}] % 26 = {p2} ({nc2})",
            'output': f"{nc1}{nc2}"
        })
        
    return "".join(plaintext_chars), steps
