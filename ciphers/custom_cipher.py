import random
import re

def validate_custom_alphabet(custom_alphabet):
    """
    Validates that the custom alphabet contains exactly 26 unique alphabetic characters.
    Returns the cleaned, uppercase alphabet string or raises ValueError.
    """
    cleaned = re.sub(r'[^A-Za-z]', '', custom_alphabet).upper()
    if len(cleaned) != 26:
        raise ValueError("Custom alphabet must contain exactly 26 alphabetic characters.")
    if len(set(cleaned)) != 26:
        raise ValueError("Custom alphabet must contain 26 unique characters (no duplicates).")
    return cleaned

def generate_random_alphabet():
    """
    Generates a randomly shuffled 26-letter alphabet.
    """
    alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    random.shuffle(alphabet)
    return "".join(alphabet)

def encrypt(plaintext, custom_alphabet):
    """
    Encrypts plaintext using Custom Substitution Cipher.
    Returns (ciphertext, steps)
    """
    custom_alphabet = validate_custom_alphabet(custom_alphabet)
    normal_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    ciphertext = []
    steps = []
    
    # Store mapping details
    mapping = {normal_alphabet[i]: custom_alphabet[i] for i in range(26)}
    
    for char in plaintext:
        if char.isalpha():
            is_upper = char.isupper()
            upper_char = char.upper()
            mapped_char = mapping[upper_char]
            final_char = mapped_char if is_upper else mapped_char.lower()
            ciphertext.append(final_char)
            steps.append({
                'char': char,
                'op': f"Replace '{char}' with '{final_char}' based on custom alphabet mapping",
                'result': final_char
            })
        else:
            ciphertext.append(char)
            steps.append({
                'char': char,
                'op': "Non-alphabetic character, kept unchanged",
                'result': char
            })
            
    return "".join(ciphertext), steps

def decrypt(ciphertext, custom_alphabet):
    """
    Decrypts ciphertext using Custom Substitution Cipher.
    Returns (plaintext, steps)
    """
    custom_alphabet = validate_custom_alphabet(custom_alphabet)
    normal_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    plaintext = []
    steps = []
    
    # Reverse mapping details
    rev_mapping = {custom_alphabet[i]: normal_alphabet[i] for i in range(26)}
    
    for char in ciphertext:
        if char.isalpha():
            is_upper = char.isupper()
            upper_char = char.upper()
            mapped_char = rev_mapping[upper_char]
            final_char = mapped_char if is_upper else mapped_char.lower()
            plaintext.append(final_char)
            steps.append({
                'char': char,
                'op': f"Replace '{char}' with '{final_char}' based on reverse mapping",
                'result': final_char
            })
        else:
            plaintext.append(char)
            steps.append({
                'char': char,
                'op': "Non-alphabetic character, kept unchanged",
                'result': char
            })
            
    return "".join(plaintext), steps
