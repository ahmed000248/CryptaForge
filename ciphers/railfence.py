import re

def encrypt(plaintext, key):
    """
    Encrypts plaintext using Rail Fence Cipher with a given number of rails (key).
    Returns (ciphertext, steps)
    """
    try:
        rails = int(key)
    except ValueError:
        raise ValueError("Rail Fence key must be an integer.")
        
    if rails < 2:
        raise ValueError("Rail Fence key must be at least 2.")
        
    text_clean = re.sub(r'[^A-Z]', '', plaintext.upper())
    if not text_clean:
        raise ValueError("Plaintext must contain at least one alphabetic character.")
        
    # Create empty grid
    grid = [['.' for _ in range(len(text_clean))] for _ in range(rails)]
    
    # Fill grid in zig-zag pattern
    row, col = 0, 0
    direction_down = False
    
    for char in text_clean:
        # Check direction
        if row == 0 or row == rails - 1:
            direction_down = not direction_down
            
        grid[row][col] = char
        col += 1
        
        if direction_down:
            row += 1
        else:
            row -= 1
            
    # Read row by row to build ciphertext
    ciphertext_chars = []
    row_details = []
    for r in range(rails):
        row_str = "".join([grid[r][c] for c in range(len(text_clean)) if grid[r][c] != '.'])
        ciphertext_chars.append(row_str)
        row_details.append({
            'rail_index': r,
            'chars': row_str
        })
        
    ciphertext = "".join(ciphertext_chars)
    
    steps = [
        {
            'type': 'zig_zag',
            'grid': grid,
            'rails': rails,
            'length': len(text_clean)
        },
        {
            'type': 'details',
            'row_details': row_details
        }
    ]
    
    return ciphertext, steps

def decrypt(ciphertext, key):
    """
    Decrypts ciphertext using Rail Fence Cipher with a given number of rails (key).
    Returns (plaintext, steps)
    """
    try:
        rails = int(key)
    except ValueError:
        raise ValueError("Rail Fence key must be an integer.")
        
    if rails < 2:
        raise ValueError("Rail Fence key must be at least 2.")
        
    ciphertext_clean = re.sub(r'[^A-Z]', '', ciphertext.upper())
    if not ciphertext_clean:
        raise ValueError("Ciphertext must contain at least one alphabetic character.")
        
    # Mark positions in grid with '*'
    grid = [['.' for _ in range(len(ciphertext_clean))] for _ in range(rails)]
    
    row, col = 0, 0
    direction_down = False
    
    for _ in range(len(ciphertext_clean)):
        if row == 0 or row == rails - 1:
            direction_down = not direction_down
        grid[row][col] = '*'
        col += 1
        if direction_down:
            row += 1
        else:
            row -= 1
            
    # Fill in the ciphertext characters into marked positions
    idx = 0
    for r in range(rails):
        for c in range(len(ciphertext_clean)):
            if grid[r][c] == '*' and idx < len(ciphertext_clean):
                grid[r][c] = ciphertext_clean[idx]
                idx += 1
                
    # Read grid in zig-zag pattern to reconstruct plaintext
    plaintext_chars = []
    row, col = 0, 0
    direction_down = False
    
    for _ in range(len(ciphertext_clean)):
        if row == 0 or row == rails - 1:
            direction_down = not direction_down
        plaintext_chars.append(grid[row][col])
        col += 1
        if direction_down:
            row += 1
        else:
            row -= 1
            
    plaintext = "".join(plaintext_chars)
    
    steps = [
        {
            'type': 'zig_zag_reconstructed',
            'grid': grid,
            'rails': rails,
            'length': len(ciphertext_clean)
        }
    ]
    
    return plaintext, steps
