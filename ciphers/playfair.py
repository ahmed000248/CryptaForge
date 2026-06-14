import re

def prepare_key(key):
    """
    Cleans the key, replaces J with I, removes duplicates, and generates a 5x5 matrix.
    """
    key = re.sub(r'[^A-Z]', '', key.upper()).replace('J', 'I')
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ" # J is excluded
    
    matrix_letters = []
    seen = set()
    
    # Add key characters
    for char in key:
        if char not in seen:
            seen.add(char)
            matrix_letters.append(char)
            
    # Add remaining alphabet characters
    for char in alphabet:
        if char not in seen:
            seen.add(char)
            matrix_letters.append(char)
            
    # Reshape into a 5x5 matrix
    matrix = [matrix_letters[i:i+5] for i in range(0, 25, 5)]
    return matrix

def find_position(matrix, char):
    """
    Finds the row and column of a character in the 5x5 matrix.
    """
    for r in range(5):
        for c in range(5):
            if matrix[r][c] == char:
                return r, c
    return None

def prepare_text(text):
    """
    Cleans text, replaces J with I, and splits into digraphs.
    Inserts 'X' between identical letters in a pair and appends 'X' if odd length.
    """
    text = re.sub(r'[^A-Z]', '', text.upper()).replace('J', 'I')
    if not text:
        return []
        
    digraphs = []
    i = 0
    while i < len(text):
        char1 = text[i]
        if i + 1 < len(text):
            char2 = text[i+1]
            if char1 == char2:
                digraphs.append((char1, 'X'))
                i += 1
            else:
                digraphs.append((char1, char2))
                i += 2
        else:
            digraphs.append((char1, 'X'))
            i += 1
    return digraphs

def encrypt(plaintext, key):
    """
    Encrypts plaintext using Playfair Cipher with a string key.
    Returns (ciphertext, steps)
    """
    if not key or not re.sub(r'[^A-Z]', '', key.upper()):
        raise ValueError("Playfair key must contain at least one alphabetic character.")

    matrix = prepare_key(key)
    digraphs = prepare_text(plaintext)
    
    ciphertext_pairs = []
    steps = []
    
    # Store matrix layout for frontend visualization
    steps.append({
        'type': 'matrix',
        'matrix': matrix
    })
    
    for pair in digraphs:
        c1, c2 = pair
        r1, col1 = find_position(matrix, c1)
        r2, col2 = find_position(matrix, c2)
        
        rule = ""
        if r1 == r2:
            # Same row -> Shift right
            nc1 = matrix[r1][(col1 + 1) % 5]
            nc2 = matrix[r2][(col2 + 1) % 5]
            rule = "Same row: Shift right"
        elif col1 == col2:
            # Same column -> Shift down
            nc1 = matrix[(r1 + 1) % 5][col1]
            nc2 = matrix[(r2 + 1) % 5][col2]
            rule = "Same column: Shift down"
        else:
            # Rectangle -> Swap columns
            nc1 = matrix[r1][col2]
            nc2 = matrix[r2][col1]
            rule = "Rectangle swap columns"
            
        ciphertext_pairs.append(nc1 + nc2)
        steps.append({
            'type': 'pair',
            'input': f"{c1}{c2}",
            'output': f"{nc1}{nc2}",
            'rule': rule,
            'positions': f"({r1},{col1}) & ({r2},{col2}) -> ({r1 if r1==r2 else (r1+1)%5 if col1==col2 else r1},{col1+1 if r1==r2 else col1 if col1==col2 else col2}) & ({r2 if r1==r2 else (r2+1)%5 if col1==col2 else r2},{col2+1 if r1==r2 else col2 if col1==col2 else col1})"
        })
        
    return "".join(ciphertext_pairs), steps

def decrypt(ciphertext, key):
    """
    Decrypts ciphertext using Playfair Cipher with a string key.
    Returns (plaintext, steps)
    """
    if not key or not re.sub(r'[^A-Z]', '', key.upper()):
        raise ValueError("Playfair key must contain at least one alphabetic character.")

    matrix = prepare_key(key)
    
    # Clean ciphertext: should only be uppercase A-Z
    ciphertext_clean = re.sub(r'[^A-Z]', '', ciphertext.upper()).replace('J', 'I')
    if len(ciphertext_clean) % 2 != 0:
        raise ValueError("Ciphertext length must be even for Playfair decryption.")
        
    digraphs = [(ciphertext_clean[i], ciphertext_clean[i+1]) for i in range(0, len(ciphertext_clean), 2)]
    
    plaintext_pairs = []
    steps = []
    
    # Store matrix layout for frontend visualization
    steps.append({
        'type': 'matrix',
        'matrix': matrix
    })
    
    for pair in digraphs:
        c1, c2 = pair
        r1, col1 = find_position(matrix, c1)
        r2, col2 = find_position(matrix, c2)
        
        rule = ""
        if r1 == r2:
            # Same row -> Shift left
            nc1 = matrix[r1][(col1 - 1) % 5]
            nc2 = matrix[r2][(col2 - 1) % 5]
            rule = "Same row: Shift left"
        elif col1 == col2:
            # Same column -> Shift up
            nc1 = matrix[(r1 - 1) % 5][col1]
            nc2 = matrix[(r2 - 1) % 5][col2]
            rule = "Same column: Shift up"
        else:
            # Rectangle -> Swap columns
            nc1 = matrix[r1][col2]
            nc2 = matrix[r2][col1]
            rule = "Rectangle swap columns"
            
        plaintext_pairs.append(nc1 + nc2)
        steps.append({
            'type': 'pair',
            'input': f"{c1}{c2}",
            'output': f"{nc1}{nc2}",
            'rule': rule,
            'positions': f"({r1},{col1}) & ({r2},{col2}) -> ({r1 if r1==r2 else (r1-1)%5 if col1==col2 else r1},{col1-1 if r1==r2 else col1 if col1==col2 else col2}) & ({r2 if r1==r2 else (r2-1)%5 if col1==col2 else r2},{col2-1 if r1==r2 else col2 if col1==col2 else col1})"
        })
        
    return "".join(plaintext_pairs), steps
