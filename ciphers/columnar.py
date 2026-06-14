import re

def get_col_order(key):
    """
    Returns the order of column indices to read/write based on alphabetical order of key characters.
    Uses stable sorting to handle duplicate characters in the key.
    """
    key_upper = key.upper()
    indexed_key = list(enumerate(key_upper))
    # Sort by character value
    sorted_indexed_key = sorted(indexed_key, key=lambda x: x[1])
    return [item[0] for item in sorted_indexed_key]

def encrypt(plaintext, key):
    """
    Encrypts plaintext using Columnar Transposition Cipher with a string key.
    Returns (ciphertext, steps)
    """
    # Clean key to uppercase letters only
    key_clean = re.sub(r'[^A-Z]', '', key.upper())
    if not key_clean:
        raise ValueError("Key must contain at least one alphabetic character.")
        
    num_cols = len(key_clean)
    
    # Clean plaintext
    text_clean = re.sub(r'[^A-Z]', '', plaintext.upper())
    if not text_clean:
        raise ValueError("Plaintext must contain at least one alphabetic character.")
        
    # Pad plaintext with 'X' to fit the grid
    original_len = len(text_clean)
    if len(text_clean) % num_cols != 0:
        padding_needed = num_cols - (len(text_clean) % num_cols)
        text_clean += 'X' * padding_needed
        
    num_rows = len(text_clean) // num_cols
    
    # Create the grid
    grid = []
    for r in range(num_rows):
        row = [text_clean[r * num_cols + c] for c in range(num_cols)]
        grid.append(row)
        
    col_order = get_col_order(key_clean)
    
    # Build ciphertext by reading columns in alphabetical order of key
    ciphertext_parts = []
    col_details = []
    for col_idx in col_order:
        col_chars = [grid[r][col_idx] for r in range(num_rows)]
        col_str = "".join(col_chars)
        ciphertext_parts.append(col_str)
        col_details.append({
            'key_char': key_clean[col_idx],
            'col_index': col_idx,
            'chars': col_str
        })
        
    ciphertext = "".join(ciphertext_parts)
    
    steps = [
        {
            'type': 'grid',
            'key': list(key_clean),
            'grid': grid,
            'col_order': col_order
        },
        {
            'type': 'details',
            'col_details': col_details
        }
    ]
    
    return ciphertext, steps

def decrypt(ciphertext, key):
    """
    Decrypts ciphertext using Columnar Transposition Cipher with a string key.
    Returns (plaintext, steps)
    """
    key_clean = re.sub(r'[^A-Z]', '', key.upper())
    if not key_clean:
        raise ValueError("Key must contain at least one alphabetic character.")
        
    num_cols = len(key_clean)
    
    ciphertext_clean = re.sub(r'[^A-Z]', '', ciphertext.upper())
    if not ciphertext_clean:
        raise ValueError("Ciphertext must contain at least one alphabetic character.")
        
    if len(ciphertext_clean) % num_cols != 0:
        raise ValueError("Ciphertext length must be a multiple of the key length.")
        
    num_rows = len(ciphertext_clean) // num_cols
    col_order = get_col_order(key_clean)
    
    # Reconstruct columns
    cols = {}
    idx = 0
    for col_idx in col_order:
        cols[col_idx] = ciphertext_clean[idx : idx + num_rows]
        idx += num_rows
        
    # Reconstruct grid
    grid = []
    for r in range(num_rows):
        row = [cols[c][r] for c in range(num_cols)]
        grid.append(row)
        
    # Read grid row by row
    plaintext_chars = []
    for r in range(num_rows):
        plaintext_chars.extend(grid[r])
        
    plaintext = "".join(plaintext_chars)
    
    steps = [
        {
            'type': 'grid_reconstructed',
            'key': list(key_clean),
            'grid': grid,
            'col_order': col_order
        }
    ]
    
    return plaintext, steps
