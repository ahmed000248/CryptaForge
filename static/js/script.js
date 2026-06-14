// JavaScript Utility Functions for Encryption-Decryption Web Application

document.addEventListener('DOMContentLoaded', function() {
    // 1. Dark Mode Logic
    const currentTheme = localStorage.getItem('theme') || 'light';
    if (currentTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        const themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
            themeIcon.classList.remove('bi-moon-fill');
            themeIcon.classList.add('bi-sun-fill');
        }
    }

    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            let theme = document.documentElement.getAttribute('data-theme');
            const themeIcon = document.getElementById('theme-icon');
            if (theme === 'dark') {
                document.documentElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
                if (themeIcon) {
                    themeIcon.classList.remove('bi-sun-fill');
                    themeIcon.classList.add('bi-moon-fill');
                }
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                if (themeIcon) {
                    themeIcon.classList.remove('bi-moon-fill');
                    themeIcon.classList.add('bi-sun-fill');
                }
            }
        });
    }

    // 2. Auto Dismiss Flash Messages
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // 3. Dynamic Key Input helper based on Cipher Selection
    const cipherSelect = document.getElementById('cipher_select');
    const keyInput = document.getElementById('key_input');
    const keyHelp = document.getElementById('key_help');
    const customCipherSelect = document.getElementById('custom_cipher_select_div');
    const regularKeySelect = document.getElementById('regular_key_div');
    const cipherBadge = document.getElementById('cipher-strength-badge');
    const cipherRecText = document.getElementById('cipher-recommendation-text');
    
    // Cipher metadata
    const cipherMeta = {
        'caesar': {
            placeholder: "e.g., 3",
            help: "Caesar key must be an integer. It shifts each letter of your message by this number.",
            badgeClass: "bg-danger",
            badgeText: "Very Weak",
            recText: "For Simplicity: Caesar is excellent for absolute beginners to understand the concept of key shifts, but offers virtually no security."
        },
        'playfair': {
            placeholder: "e.g., KEYWORD",
            help: "Playfair key must be a text keyword. It constructs a 5x5 grid using the letters of this word.",
            badgeClass: "bg-warning text-dark",
            badgeText: "Weak",
            recText: "For Learning: Playfair is a digraph substitution cipher. Great for learning grid-based letter mapping and handling duplicates."
        },
        'hill': {
            placeholder: "e.g., HILL or 7,8,11,11",
            help: "Hill key must be a 4-letter word or 4 comma-separated integers. It builds a 2x2 matrix that must be invertible modulo 26.",
            badgeClass: "bg-info text-dark",
            badgeText: "Moderate",
            recText: "For Better Classical Security: Hill cipher uses matrix multiplication and is harder to crack, making it a great math-based classical cipher."
        },
        'columnar': {
            placeholder: "e.g., GERMAN",
            help: "Columnar key must be a text keyword. It arranges the message in rows and outputs it column-by-column in alphabetical key order.",
            badgeClass: "bg-info text-dark",
            badgeText: "Moderate",
            recText: "For Learning: Columnar transposition rearranges letter positions rather than substituting them. Great for learning structural permutation."
        },
        'railfence': {
            placeholder: "e.g., 3",
            help: "Rail Fence key must be an integer >= 2. It represents the number of horizontal 'rails' to write the letters in a zig-zag.",
            badgeClass: "bg-warning text-dark",
            badgeText: "Weak",
            recText: "For Simplicity: Rail Fence is a simple transposition cipher that uses a zig-zag pattern. Easy to visualize but easily crackable."
        },
        'custom': {
            placeholder: "Select custom cipher below",
            help: "Select one of your saved custom substitution alphabets.",
            badgeClass: "bg-secondary",
            badgeText: "Custom (Depends on Design)",
            recText: "For Experimentation: Custom alphabets allow monoalphabetic substitution. The security depends on key secrecy and custom mapping design."
        }
    };

    function updateCipherUI(selected) {
        if (!selected) return;
        
        // Handle showing/hiding custom cipher selectors
        if (selected === 'custom') {
            if (customCipherSelect) customCipherSelect.classList.remove('d-none');
            if (regularKeySelect) regularKeySelect.classList.add('d-none');
            if (keyInput) keyInput.removeAttribute('required');
        } else {
            if (customCipherSelect) customCipherSelect.classList.add('d-none');
            if (regularKeySelect) regularKeySelect.classList.remove('d-none');
            if (keyInput) {
                keyInput.setAttribute('required', 'required');
                keyInput.placeholder = cipherMeta[selected].placeholder;
            }
            if (keyHelp) {
                keyHelp.textContent = cipherMeta[selected].help;
            }
        }

        // Update badges
        if (cipherBadge && cipherMeta[selected]) {
            cipherBadge.className = "badge " + cipherMeta[selected].badgeClass;
            cipherBadge.textContent = cipherMeta[selected].badgeText;
        }

        // Update recommendations
        if (cipherRecText && cipherMeta[selected]) {
            cipherRecText.textContent = cipherMeta[selected].recText;
        }
    }

    if (cipherSelect) {
        cipherSelect.addEventListener('change', function() {
            updateCipherUI(this.value);
            
            // Pop up information modal if it exists
            const infoModalElement = document.getElementById(this.value + 'InfoModal');
            if (infoModalElement) {
                const infoModal = new bootstrap.Modal(infoModalElement);
                infoModal.show();
            }
        });
        // Initial setup on load
        updateCipherUI(cipherSelect.value);
    }
});

// 4. Copy to Clipboard Function
function copyToClipboard(elementId, btn) {
    const textElement = document.getElementById(elementId);
    if (!textElement) return;

    let textToCopy = textElement.value || textElement.textContent;
    
    navigator.clipboard.writeText(textToCopy).then(function() {
        // Change button icon/text temporary
        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-check2"></i> Copied!';
        btn.classList.remove('btn-outline-primary', 'btn-outline-secondary');
        btn.classList.add('btn-success');
        
        setTimeout(function() {
            btn.innerHTML = originalHTML;
            btn.classList.remove('btn-success');
            btn.classList.add('btn-outline-secondary');
        }, 2000);
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
    });
}

// 5. Clear Form Function
function clearForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
        // Clear result containers if any
        const resultCard = document.getElementById('result-card');
        if (resultCard) {
            resultCard.classList.add('d-none');
        }
    }
}

// 6. Custom Cipher Alphabet Generator (Lab)
function generateRandomAlphabet() {
    const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
    for (let i = alphabet.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [alphabet[i], alphabet[j]] = [alphabet[j], alphabet[i]];
    }
    const customAlphabetStr = alphabet.join("");
    
    const customAlphabetInput = document.getElementById('custom_alphabet');
    if (customAlphabetInput) {
        customAlphabetInput.value = customAlphabetStr;
        // Trigger input event to update mapping preview
        customAlphabetInput.dispatchEvent(new Event('input'));
    }
}

// 7. Dynamic Map Preview for Custom Cipher Lab
function updateMappingPreview(inputElement) {
    const customAlph = inputElement.value.toUpperCase().replace(/[^A-Z]/g, '');
    inputElement.value = customAlph; // update input text to clean uppercase letters
    
    const normalAlphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const previewContainer = document.getElementById('mapping-preview');
    if (!previewContainer) return;
    
    previewContainer.innerHTML = '';
    
    for (let i = 0; i < 26; i++) {
        const normalChar = normalAlphabet[i];
        const customChar = customAlph[i] || '_';
        
        const cell = document.createElement('div');
        cell.className = 'text-center border p-1 rounded bg-light m-1';
        cell.style.minWidth = '40px';
        cell.style.flex = '1 0 7%';
        cell.innerHTML = `<small class="text-muted d-block">${normalChar}</small><strong>${customChar}</strong>`;
        previewContainer.appendChild(cell);
    }
}
