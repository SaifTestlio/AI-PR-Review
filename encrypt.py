#!/usr/bin/env python3
"""
Command line utility for encrypting and decrypting strings using the SecretManager.

Usage:
    Encryption: python encrypt.py --text <text_to_encrypt> [--key <encryption_key>]
    Decryption: python encrypt.py --text <text_to_decrypt> --key <encryption_key> --decrypt
"""
import argparse
import sys
from cryptography.fernet import InvalidToken

from lib.utils.cryptography import SecretManager

def main():
    """Encrypt or decrypt a string using Fernet encryption"""
    parser = argparse.ArgumentParser(
        description='Encrypt or decrypt a string using Fernet encryption'
    )
    parser.add_argument(
        '--key',
        required=False,
        help='Fernet encryption key (required for decryption)'
    )
    parser.add_argument('--text', required=True, help='Text to encrypt/decrypt')
    parser.add_argument('--decrypt', action='store_true', help='Decrypt mode')

    args = parser.parse_args()

    if args.decrypt and not args.key:
        print("Error: Decryption requires a key", file=sys.stderr)
        sys.exit(1)

    key = args.key if args.key else SecretManager.generate_key()

    try:
        secret_manager = SecretManager(key)
        if args.decrypt:
            result = secret_manager.decrypt(args.text)
            print(f"Decrypted text: {result}")
        else:
            encrypted = secret_manager.encrypt(args.text)
            if not args.key:
                print(f"Generated key: {key}")
            print(f"Encrypted text: {encrypted}")
    except (ValueError, InvalidToken) as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
