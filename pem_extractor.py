#!/usr/bin/env python3
"""
PEM File Extraction Script
Extracts certificate (.crt) and private key (.key) from a PEM file.
"""

import re
import os
import sys

def extract_from_pem(pem_file_path, output_prefix="client"):
    """
    Extract certificate and private key from PEM file.
    
    Args:
        pem_file_path (str): Path to the PEM file
        output_prefix (str): Prefix for output files
    """
    
    if not os.path.exists(pem_file_path):
        print(f"Error: PEM file '{pem_file_path}' not found")
        return False
    
    try:
        with open(pem_file_path, 'r') as f:
            content = f.read()
        
        # Extract certificate (public key)
        cert_pattern = r'-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----'
        cert_matches = re.findall(cert_pattern, content, re.DOTALL)
        
        # Extract private key
        key_patterns = [
            r'-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----',
            r'-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----',
            r'-----BEGIN EC PRIVATE KEY-----.*?-----END EC PRIVATE KEY-----',
            r'-----BEGIN ENCRYPTED PRIVATE KEY-----.*?-----END ENCRYPTED PRIVATE KEY-----'
        ]
        
        key_matches = []
        for pattern in key_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            key_matches.extend(matches)
        
        # Save certificate
        if cert_matches:
            cert_file = f"{output_prefix}.crt"
            with open(cert_file, 'w') as f:
                for cert in cert_matches:
                    f.write(cert + '\n')
            print(f"Certificate saved to: {cert_file}")
        else:
            print("No certificate found in PEM file")
        
        # Save private key
        if key_matches:
            key_file = f"{output_prefix}.key"
            with open(key_file, 'w') as f:
                for key in key_matches:
                    f.write(key + '\n')
            print(f"Private key saved to: {key_file}")
            
            # Set restrictive permissions on private key file
            os.chmod(key_file, 0o600)
            print(f"Set permissions 600 on {key_file}")
        else:
            print("No private key found in PEM file")
        
        return bool(cert_matches and key_matches)
        
    except Exception as e:
        print(f"Error processing PEM file: {e}")
        return False

def analyze_pem_file(pem_file_path):
    """
    Analyze the contents of a PEM file to show what's inside.
    """
    
    if not os.path.exists(pem_file_path):
        print(f"Error: PEM file '{pem_file_path}' not found")
        return
    
    try:
        with open(pem_file_path, 'r') as f:
            content = f.read()
        
        print(f"Analyzing PEM file: {pem_file_path}")
        print("=" * 50)
        
        # Check for different types of content
        items_found = []
        
        if '-----BEGIN CERTIFICATE-----' in content:
            cert_count = content.count('-----BEGIN CERTIFICATE-----')
            items_found.append(f"Certificate(s): {cert_count}")
        
        if '-----BEGIN PRIVATE KEY-----' in content:
            items_found.append("Private Key (PKCS#8)")
        
        if '-----BEGIN RSA PRIVATE KEY-----' in content:
            items_found.append("RSA Private Key")
        
        if '-----BEGIN EC PRIVATE KEY-----' in content:
            items_found.append("EC Private Key")
        
        if '-----BEGIN ENCRYPTED PRIVATE KEY-----' in content:
            items_found.append("Encrypted Private Key")
        
        if '-----BEGIN PUBLIC KEY-----' in content:
            items_found.append("Public Key")
        
        if '-----BEGIN CERTIFICATE REQUEST-----' in content:
            items_found.append("Certificate Request (CSR)")
        
        if items_found:
            print("Contents found:")
            for item in items_found:
                print(f"  - {item}")
        else:
            print("No recognized PEM content found")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"Error analyzing PEM file: {e}")

def main():
    """
    Main function with command line support.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract certificate and key from PEM file')
    parser.add_argument('pem_file', help='Path to the PEM file')
    parser.add_argument('--output', '-o', default='client', help='Output file prefix (default: client)')
    parser.add_argument('--analyze', '-a', action='store_true', help='Analyze PEM file contents')
    
    args = parser.parse_args()
    
    if args.analyze:
        analyze_pem_file(args.pem_file)
    
    print()
    success = extract_from_pem(args.pem_file, args.output)
    
    if success:
        print("\nExtraction completed successfully!")
        print(f"You can now use: --cert {args.output}.crt --key {args.output}.key")
    else:
        print("\nExtraction failed or incomplete")

if __name__ == "__main__":
    main()
