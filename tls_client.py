#!/usr/bin/env python3
"""
Optimized TLS Protocol Client Implementation
Implements the challenge-response protocol with proof-of-work authentication.
"""

import ssl
import socket
import hashlib
import secrets
import string
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sys
import os

class OptimizedTLSClient:
    def __init__(self, host="18.202.148.130", port=3336, cert_path=None, key_path=None):
        self.host = host
        self.port = port
        self.cert_path = cert_path
        self.key_path = key_path
        self.conn = None
        self.authdata = ""
        
        # Pre-compiled character set for random string generation (excluding \n\r\t )
        self.valid_chars = ''.join(c for c in (chr(i) for i in range(32, 127)) 
                                  if c not in '\n\r\t ')
        
        # Personal information - UPDATE THESE WITH YOUR ACTUAL DETAILS
        self.personal_info = {
            'name': 'Anil Kumar Dasari',
            'emails': ['dak.dba@gmail.com'],
            'skype': 'N/A',  # or 'N/A' if no Skype
            'birthdate': '11.07.1980',  # format: %d.%m.%Y
            'country': 'India',
            'address_lines': ['Whitefield', 'Benguluru', 'Karnataka', '560066']
        }
    
    def tls_connect(self):
        """Establish TLS connection with client certificates"""
        try:
            # Create SSL context
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Load client certificate and key if provided
            if self.cert_path and self.key_path:
                context.load_cert_chain(self.cert_path, self.key_path)
            
            # Create socket and wrap with SSL
            sock = socket.create_connection((self.host, self.port), timeout=30)
            self.conn = context.wrap_socket(sock, server_hostname=self.host)
            
            print(f"Connected to {self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def read_line(self):
        """Read a line from the connection"""
        try:
            data = b''
            while True:
                chunk = self.conn.recv(1)
                if not chunk:
                    break
                data += chunk
                if chunk == b'\n':
                    break
            return data.decode('utf-8').strip()
        except Exception as e:
            print(f"Read error: {e}")
            return ""
    
    def write_line(self, data):
        """Write a line to the connection"""
        try:
            self.conn.sendall((data + '\n').encode('utf-8'))
            return True
        except Exception as e:
            print(f"Write error: {e}")
            return False
    
    def generate_random_string(self, length=8):
        """Generate random string with valid characters"""
        return ''.join(secrets.choice(self.valid_chars) for _ in range(length))
    
    def sha1_hash(self, data):
        """Calculate SHA1 hash and return hex string"""
        return hashlib.sha1(data.encode('utf-8')).hexdigest()
    
    def pow_worker(self, authdata, difficulty, result_queue, stop_event):
        """Worker function for proof-of-work calculation"""
        target = '0' * int(difficulty)
        
        while not stop_event.is_set():
            # Generate random suffix of varying length for better distribution
            suffix = self.generate_random_string(secrets.randbelow(8) + 4)
            cksum = self.sha1_hash(authdata + suffix)
            
            if cksum.startswith(target):
                result_queue.put(suffix)
                stop_event.set()
                return
            
            # Check every 10000 iterations to avoid busy waiting
            if secrets.randbelow(10000) == 0:
                time.sleep(0.001)
    
    def solve_proof_of_work(self, authdata, difficulty):
        """Solve proof-of-work using multiple threads"""
        print(f"Solving proof-of-work (difficulty: {difficulty})...")
        start_time = time.time()

        # # Use multiple threads for parallel processing
        # num_threads = min(multiprocessing.cpu_count(), 32)  # Limit to 32 threads
        # print(f"Using {num_threads} threads for proof-of-work")

        # Use more threads for better parallelism
        cpu_count = multiprocessing.cpu_count()
        print(f"CPU cores available: {cpu_count}")
        num_threads = min(cpu_count * 2, 32)  # Up to 32 threads
        print(f"Using {num_threads} threads for proof-of-work")

        result_queue = []
        stop_event = threading.Event()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for _ in range(num_threads):
                future = executor.submit(self.pow_worker, authdata, difficulty, result_queue, stop_event)
                futures.append(future)
            
            # Wait for first result
            while not stop_event.is_set() and not result_queue:
                time.sleep(0.1)
            
            if result_queue:
                solution = result_queue[0]
                elapsed = time.time() - start_time
                print(f"Proof-of-work solved in {elapsed:.2f} seconds")
                return solution
        
        return None
    
    def create_authenticated_response(self, nonce, data):
        """Create authenticated response with SHA1 hash"""
        return self.sha1_hash(self.authdata + nonce) + " " + data
    
    def handle_command(self, args):
        """Handle server commands"""
        cmd = args[0]
        
        if cmd == "HELO":
            return self.write_line("TOAKUEI")
        
        elif cmd == "ERROR":
            print("ERROR: " + " ".join(args[1:]))
            return False
        
        elif cmd == "POW":
            self.authdata = args[1]
            difficulty = args[2]
            solution = self.solve_proof_of_work(self.authdata, difficulty)
            if solution:
                return self.write_line(solution)
            else:
                print("Failed to solve proof-of-work")
                return False
        
        elif cmd == "END":
            print("Data submission confirmed")
            return self.write_line("OK")
        
        elif cmd == "NAME":
            response = self.create_authenticated_response(args[1], self.personal_info['name'])
            return self.write_line(response)
        
        elif cmd == "MAILNUM":
            response = self.create_authenticated_response(args[1], str(len(self.personal_info['emails'])))
            return self.write_line(response)
        
        elif cmd.startswith("MAIL"):
            mail_idx = int(cmd[4:]) - 1
            if mail_idx < len(self.personal_info['emails']):
                email = self.personal_info['emails'][mail_idx]
                response = self.create_authenticated_response(args[1], email)
                return self.write_line(response)
            return False
        
        elif cmd == "SKYPE":
            response = self.create_authenticated_response(args[1], self.personal_info['skype'])
            return self.write_line(response)
        
        elif cmd == "BIRTHDATE":
            response = self.create_authenticated_response(args[1], self.personal_info['birthdate'])
            return self.write_line(response)
        
        elif cmd == "COUNTRY":
            response = self.create_authenticated_response(args[1], self.personal_info['country'])
            return self.write_line(response)
        
        elif cmd == "ADDRNUM":
            response = self.create_authenticated_response(args[1], str(len(self.personal_info['address_lines'])))
            return self.write_line(response)
        
        elif cmd.startswith("ADDRLINE"):
            addr_idx = int(cmd[8:]) - 1
            if addr_idx < len(self.personal_info['address_lines']):
                addr_line = self.personal_info['address_lines'][addr_idx]
                response = self.create_authenticated_response(args[1], addr_line)
                return self.write_line(response)
            return False
        
        else:
            print(f"Unknown command: {cmd}")
            return False
    
    def run(self):
        """Main protocol loop"""
        if not self.tls_connect():
            return False
        
        try:
            print("Starting protocol communication...")
            
            while True:
                # Read command from server
                line = self.read_line()
                if not line:
                    print("Connection closed by server")
                    break
                
                print(f"Received: {line}")
                args = line.split(' ')
                
                # Handle command
                if not self.handle_command(args):
                    break
                
                # Check for END command
                if args[0] == "END":
                    print("Protocol completed successfully")
                    break
            
            return True
            
        except Exception as e:
            print(f"Protocol error: {e}")
            return False
        
        finally:
            if self.conn:
                self.conn.close()
                print("Connection closed")

def main():
    """Main function with command line argument support"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TLS Protocol Client')
    parser.add_argument('--host', default='18.202.148.130', help='Server hostname')
    parser.add_argument('--port', type=int, default=3336, help='Server port')
    parser.add_argument('--cert', help='Client certificate file path')
    parser.add_argument('--key', help='Client private key file path')
    
    args = parser.parse_args()

    
    # Create and run client
    client = OptimizedTLSClient(
        host=args.host,
        port=args.port,
        cert_path=args.cert,
        key_path=args.key
    )
    
    print("=== TLS Protocol Client ===")
    print(f"Connecting to {args.host}:{args.port}")
    
    if client.run():
        print("Client completed successfully")
        sys.exit(0)
    else:
        print("Client failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
