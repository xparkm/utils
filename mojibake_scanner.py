import os
import sys
import re
import unicodedata

# Unicode range for the standard Cyrillic alphabet
CYRILLIC_RANGE = r'[\u0400-\u04FF]'

def try_fix_and_detect(corrupted_name):
    """
    Attempts to fix the Mojibake and returns the corrected name if 
    it successfully converts Latin-based corruption into Cyrillic.
    """
    # 1. NORMALIZE UNICODE (The Fix for 'Oeoiie...')
    # This combines letters + accents back into single characters.
    # e.g., 'O' + '`' becomes 'Ò' (which CP1252 can understand).
    corrupted_name = unicodedata.normalize('NFC', corrupted_name)

    # 2. ARTIFACT REPLACEMENT
    replacements = {
        'ﬂ': '\u00fe',  # ﬂ -> þ (0xFE) -> ю
        '›': '\u00f0',  # › -> ð (0xF0) -> р
        '‹': '\u00d0',  # ‹ -> Ð (0xD0) -> Р
        '‡': '\u00dd',  # ‡ -> Ý (0xDD) -> Э
        '†': '\u00c9',  # † -> É (0xC9) -> Й
        '◊': '\u00d7',  # ◊ -> × (0xD7) -> Ч
    }
    
    clean_name = corrupted_name
    for artifact, fix in replacements.items():
        clean_name = clean_name.replace(artifact, fix)

    # 3. CORE DECODE LOGIC
    try:
        # Encode with CP1252 (the viewing code page) to get the raw bytes
        raw_bytes = clean_name.encode('cp1252', errors='ignore')
        # Decode the bytes with CP1251 (the original code page)
        decoded_name = raw_bytes.decode('cp1251', errors='replace')
        
        # 3. VALIDATION HEURISTIC
        # Check if the corrected name now contains Cyrillic characters.
        if re.search(CYRILLIC_RANGE, decoded_name):
            # To avoid false positives (e.g., file name already containing Cyrillic), 
            # we ensure the original name did *not* contain standard Cyrillic.
            if not re.search(CYRILLIC_RANGE, corrupted_name):
                return decoded_name

    except Exception as e:
        # If encoding/decoding fails (e.g., strict mapping errors), it's not our mojibake pattern.
        print(e)
        pass
    
    return None # Not detected as this type of mojibake


def scan_for_mojibake(root_dir):
    """
    Scans the directory structure starting at root_dir for Mojibake filenames.
    """
    print(f"--- Scanning directory: {root_dir} ---")
    
    found_count = 0
    
    # os.walk traverses the tree, returning (dirpath, dirnames, filenames)
    for root, dirs, files in os.walk(root_dir):

        # Check directories first
        for name in dirs:
            fixed_name = try_fix_and_detect(name)
            if fixed_name:
                print(f"[DIR] CORRUPTED: {os.path.join(root, name)}")
                print(f"      FIXED:     {os.path.join(root, fixed_name)}")
                found_count += 1
                
        # Check files
        for name in files:
            fixed_name = try_fix_and_detect(name)
            if fixed_name:
                print(f"[FILE] CORRUPTED: {os.path.join(root, name)}")
                print(f"       FIXED:     {os.path.join(root, fixed_name)}")
                found_count += 1
                
    if found_count > 0:
        print(f"\nScan complete. Found {found_count} mojibake entries.")
    else:
        print("\nScan complete. No mojibake filenames detected.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default to the current directory if no argument is provided
        scan_dir = os.getcwd()
    else:
        scan_dir = sys.argv[1]
    
    # Ensure the path exists before starting
    if not os.path.isdir(scan_dir):
        print(f"Error: Directory not found: {scan_dir}")
        sys.exit(1)
        
    scan_for_mojibake(scan_dir)
