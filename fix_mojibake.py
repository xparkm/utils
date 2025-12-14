import sys
import argparse
import unicodedata



def fix_mojibake(text):
    """
    Decodes text corrupted by Windows-1251 -> Windows-1252 interpretation.
    Handles NFD normalization (macOS style) and known artifacts.
    """
    if not text:
        return ""

    # 1. NORMALIZE UNICODE (The Fix for 'Oeoiie...')
    # This combines letters + accents back into single characters.
    # e.g., 'O' + '`' becomes 'Ò' (which CP1252 can understand).
    text = unicodedata.normalize('NFC', text)

    # 2. ARTIFACT REPLACEMENT
    replacements = {
        'ﬂ': '\u00fe',  # ﬂ -> þ (0xFE) -> ю
        '›': '\u00f0',  # › -> ð (0xF0) -> р
        '‹': '\u00d0',  # ‹ -> Ð (0xD0) -> Р
        '‡': '\u00dd',  # ‡ -> Ý (0xDD) -> Э
        '†': '\u00c9',  # † -> É (0xC9) -> Й
        '◊': '\u00d7',  # ◊ -> × (0xD7) -> Ч
    }
    
    clean_text = text
    for artifact, fix in replacements.items():
        clean_text = clean_text.replace(artifact, fix)

    # 3. CORE DECODE LOGIC
    try:
        # Use 'ignore' to drop any invisible non-CP1252 junk that survives normalization
        raw_bytes = clean_text.encode('cp1252', errors='ignore') 
        
        # Use 'replace' to ensure valid output even if a byte is weird
        decoded_name = raw_bytes.decode('cp1251', errors='replace')
        
        return decoded_name
    except Exception:
        return f"[Error: Could not decode]"


def main():
    # Setup command line argument parsing
    parser = argparse.ArgumentParser(description="Decode corrupted Cyrillic (Mojibake) strings.")
    parser.add_argument('input_text', nargs='?', help="The corrupted string to decode")
    args = parser.parse_args()

    # MODE 1: Command Line Argument provided
    if args.input_text:
        print(fix_mojibake(args.input_text))

    # MODE 2: Piped input (e.g., from a file or another command)
    elif not sys.stdin.isatty():
        for line in sys.stdin:
            # Process line by line, stripping newline characters
            print(fix_mojibake(line.strip()))

    # MODE 3: Interactive Mode (User types input)
    else:
        print("--- Interactive Mojibake Decoder ---")
        print("Type corrupted text and press Enter. Press Ctrl+C to exit.")
        try:
            while True:
                user_input = input(">> ")
                if user_input.lower() in ['exit', 'quit']:
                    break
                print(f"=> {fix_mojibake(user_input)}")
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)

if __name__ == "__main__":
    main()
