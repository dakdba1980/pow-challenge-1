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
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import time
import sys
import os
import queue

def pow_worker_function(args):
    """Multiprocessing worker function for proof-of-work calculation"""
    authdata, difficulty, worker_id, batch_size = args
    target = '0' * int(difficulty)
    local_counter = 0
    
    # Use different character sets for different workers to reduce collision
    charset = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    
    # Each worker uses a different random seed
    random_gen = secrets.SystemRandom(worker_id + time.time_ns())
    
    start_time = time.time()
    timeout = 300  # 5 minutes timeout per worker
    
    while local_counter < batch_size and (time.time() - start_time) < timeout:
        # Generate candidate with varying lengths
        suffix_length = random_gen.randint(4, 12)
        suffix = ''.join(random_gen.choice(charset) for _ in range(suffix_length))
        
        # Calculate hash
        combined = authdata + suffix
        hasher = hashlib.sha1()
        hasher.update(combined.encode('utf-8'))
        cksum = hasher.hexdigest()
        
        local_counter += 1
        
        if cksum.startswith(target):
            return suffix, local_counter, True
    
    return None, local_counter, False

class OptimizedTLSClient:
    def __init__(self, host="18.202.148.130", port=3336, cert_path=None, key_path=None):
        self.host = host
        self.port = port
        self.cert_path = cert_path
        self.key_path = key_path
        self.conn = None
        self.authdata = ""
        
        # Personal information - UPDATE THESE WITH YOUR ACTUAL DETAILS
        self.personal_info = {
            'name': 'Anil Kumar Dasari',
            'emails': ['dak.dba@gmail.com'],
            'skype': 'N/A',
            'birthdate': '11.07.1980',
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
    
    def sha1_hash_optimized(self, data):
        """Optimized SHA1 hash calculation"""
        return hashlib.sha1(data.encode('utf-8')).hexdigest()
    
    def solve_proof_of_work_threaded(self, authdata, difficulty):
        """Solve proof-of-work using threading with timeout"""
        print(f"Solving proof-of-work (difficulty: {difficulty}) using threading...")
        start_time = time.time()
        target = '0' * int(difficulty)
        
        # Threading approach with proper synchronization
        result_found = threading.Event()
        result_data = {}
        total_hashes = 0
        hash_lock = threading.Lock()
        
        def worker_thread(thread_id):
            nonlocal total_hashes
            local_counter = 0
            charset = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
            random_gen = secrets.SystemRandom(thread_id + time.time_ns())
            
            while not result_found.is_set():
                suffix_length = random_gen.randint(4, 12)
                suffix = ''.join(random_gen.choice(charset) for _ in range(suffix_length))
                
                combined = authdata + suffix
                hasher = hashlib.sha1()
                hasher.update(combined.encode('utf-8'))
                cksum = hasher.hexdigest()
                
                local_counter += 1
                
                if cksum.startswith(target):
                    if not result_found.is_set():
                        result_data['suffix'] = suffix
                        result_data['hashes'] = local_counter
                        result_found.set()
                    return
                
                # Update global counter periodically
                if local_counter % 10000 == 0:
                    with hash_lock:
                        total_hashes += 10000
        
        # Start worker threads
        num_threads = min(multiprocessing.cpu_count() * 2, 16)
        threads = []
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_thread, i) for i in range(num_threads)]
            
            # Monitor progress with timeout
            timeout = 600  # 10 minutes timeout
            last_report = start_time
            
            while not result_found.is_set():
                if time.time() - start_time > timeout:
                    print("Proof-of-work timed out after 10 minutes")
                    result_found.set()
                    break
                
                time.sleep(1)
                
                # Report progress every 30 seconds
                if time.time() - last_report >= 30:
                    elapsed = time.time() - start_time
                    with hash_lock:
                        current_total = total_hashes
                    rate = current_total / elapsed if elapsed > 0 else 0
                    print(f"Progress: {current_total:,} hashes in {elapsed:.1f}s (rate: {rate:,.0f} H/s)")
                    last_report = time.time()
        
        if 'suffix' in result_data:
            elapsed = time.time() - start_time
            rate = result_data['hashes'] / elapsed if elapsed > 0 else 0
            print(f"Proof-of-work solved in {elapsed:.2f} seconds")
            print(f"Total hashes: {result_data['hashes']:,} (rate: {rate:,.0f} H/s)")
            
            # Verify solution
            verification_hash = self.sha1_hash_optimized(authdata + result_data['suffix'])
            if verification_hash.startswith(target):
                print(f"Solution verified: {result_data['suffix']}")
                return result_data['suffix']
            else:
                print("Solution verification failed!")
        
        return None
    
    def solve_proof_of_work_multiprocessing(self, authdata, difficulty):
        """Solve proof-of-work using multiprocessing with timeout"""
        print(f"Solving proof-of-work (difficulty: {difficulty}) using multiprocessing...")
        start_time = time.time()
        
        cpu_count = multiprocessing.cpu_count()
        print(f"CPU cores available: {cpu_count}")

        """Solve using multiprocessing"""
        num_workers = cpu_count
        print(f"Using {num_workers} processes for proof-of-work")        
        batch_size = 100000  # Each worker processes this many hashes before returning
        
        try:
            with ProcessPoolExecutor(max_workers=num_workers) as executor:
                timeout = 600  # 10 minutes timeout
                
                while time.time() - start_time < timeout:
                    # Submit batch of work to all workers
                    worker_args = [
                        (authdata, difficulty, i, batch_size) 
                        for i in range(num_workers)
                    ]
                    
                    # Submit all tasks
                    future_to_worker = {
                        executor.submit(pow_worker_function, args): i 
                        for i, args in enumerate(worker_args)
                    }
                    
                    # Check for completion
                    for future in as_completed(future_to_worker, timeout=60):
                        worker_id = future_to_worker[future]
                        try:
                            result, hash_count, found = future.result()
                            if found:
                                elapsed = time.time() - start_time
                                rate = hash_count / elapsed if elapsed > 0 else 0
                                print(f"Proof-of-work solved in {elapsed:.2f} seconds")
                                print(f"Total hashes: {hash_count:,} (rate: {rate:,.0f} H/s)")
                                
                                # Verify solution
                                verification_hash = self.sha1_hash_optimized(authdata + result)
                                target = '0' * int(difficulty)
                                if verification_hash.startswith(target):
                                    print(f"Solution verified: {result}")
                                    return result
                                else:
                                    print("Solution verification failed!")
                        except Exception as e:
                            print(f"Worker {worker_id} error: {e}")
                            continue
                    
                    # Report progress
                    elapsed = time.time() - start_time
                    total_hashes = num_workers * batch_size
                    rate = total_hashes / elapsed if elapsed > 0 else 0
                    print(f"Batch completed: {total_hashes:,} hashes in {elapsed:.1f}s (rate: {rate:,.0f} H/s)")
                
                print("Proof-of-work timed out after 10 minutes")
                return None
                
        except Exception as e:
            print(f"Multiprocessing error: {e}")
            return None
    
    def solve_proof_of_work_optimized(self, authdata, difficulty):
        """Optimized proof-of-work solver with fallback strategies"""
        print(f"Solving proof-of-work (difficulty: {difficulty})...")
        
        # For low difficulty, use threading
        if int(difficulty) <= 4:
            return self.solve_proof_of_work_threaded(authdata, difficulty)
        
        # For higher difficulty, try multiprocessing first, then fallback to threading
        result = self.solve_proof_of_work_multiprocessing(authdata, difficulty)
        if result is None:
            print("Multiprocessing failed, falling back to threading...")
            result = self.solve_proof_of_work_threaded(authdata, difficulty)
        
        return result
    
    def create_authenticated_response(self, nonce, data):
        """Create authenticated response with SHA1 hash"""
        return self.sha1_hash_optimized(self.authdata + nonce) + " " + data
    
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
            solution = self.solve_proof_of_work_optimized(self.authdata, difficulty)
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