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
import itertools

# Global function for multiprocessing worker (must be at module level)
def pow_worker_function(authdata, difficulty, worker_id, result_queue, stop_event, stats_counter, valid_chars):
    """Optimized worker function for proof-of-work calculation"""
    target = '0' * int(difficulty)
    local_counter = 0
    
    # Each worker starts with different random seed to avoid overlap
    local_random = secrets.SystemRandom(worker_id)
    
    while not stop_event.is_set():
        # Generate candidates more efficiently
        suffix_length = local_random.randint(4, 8)
        suffix = ''.join(local_random.choice(valid_chars) for _ in range(suffix_length))
        
        # Optimized hash calculation
        combined = authdata + suffix
        hasher = hashlib.sha1()
        hasher.update(combined.encode('utf-8'))
        cksum = hasher.hexdigest()
        
        local_counter += 1
        
        if cksum.startswith(target):
            result_queue.put((suffix, local_counter))
            stop_event.set()
            return
        
        # Update stats every 50000 iterations
        if local_counter % 50000 == 0:
            with stats_counter.get_lock():
                stats_counter.value += 50000

class OptimizedTLSClient:
    def __init__(self, host="18.202.148.130", port=3336, cert_path=None, key_path=None):
        self.host = host
        self.port = port
        self.cert_path = cert_path
        self.key_path = key_path
        self.conn = None
        self.authdata = ""
        
        # Optimized character set for random string generation
        self.valid_chars = string.ascii_letters + string.digits + string.punctuation
        self.valid_chars = ''.join(c for c in self.valid_chars if c not in '\n\r\t ')
        
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
    
    def generate_optimized_candidates(self, start_length=4, max_length=12):
        """Generate candidate strings more efficiently"""
        charset = self.valid_chars
        
        # Start with shorter lengths and gradually increase
        for length in range(start_length, max_length + 1):
            # Use itertools for systematic generation mixed with random
            if length <= 6:  # For shorter lengths, try systematic approach
                for candidate in itertools.product(charset, repeat=length):
                    yield ''.join(candidate)
            else:  # For longer lengths, use random generation
                while True:
                    yield ''.join(secrets.choice(charset) for _ in range(length))
    
    def sha1_hash_optimized(self, data):
        """Optimized SHA1 hash calculation"""
        return hashlib.sha1(data.encode('utf-8')).hexdigest()
    
    def pow_worker_threaded(self, authdata, difficulty, worker_id, result_queue, stop_event, stats_counter):
        """Threaded worker function for proof-of-work calculation"""
        target = '0' * int(difficulty)
        local_counter = 0
        
        # Each worker starts with different random seed to avoid overlap
        local_random = secrets.SystemRandom(worker_id)
        
        while not stop_event.is_set():
            # Generate candidates more efficiently
            suffix_length = local_random.randint(4, 8)
            suffix = ''.join(local_random.choice(self.valid_chars) for _ in range(suffix_length))
            
            # Optimized hash calculation
            combined = authdata + suffix
            hasher = hashlib.sha1()
            hasher.update(combined.encode('utf-8'))
            cksum = hasher.hexdigest()
            
            local_counter += 1
            
            if cksum.startswith(target):
                result_queue.put((suffix, local_counter))
                stop_event.set()
                return
            
            # Update stats every 50000 iterations
            if local_counter % 50000 == 0:
                with stats_counter.get_lock():
                    stats_counter.value += 50000
    
    def solve_proof_of_work_optimized(self, authdata, difficulty):
        """Optimized proof-of-work solver using multiprocessing and threading fallback"""
        print(f"Solving proof-of-work (difficulty: {difficulty})...")
        start_time = time.time()
        
        # Use all available CPU cores
        cpu_count = multiprocessing.cpu_count()
        print(f"CPU cores available: {cpu_count}")
        
        # Try multiprocessing first, fall back to threading if it fails
        try:
            return self._solve_with_multiprocessing(authdata, difficulty, cpu_count, start_time)
        except Exception as e:
            print(f"Multiprocessing failed ({e}), falling back to threading...")
            return self._solve_with_threading(authdata, difficulty, cpu_count * 2, start_time)
    
    def _solve_with_multiprocessing(self, authdata, difficulty, cpu_count, start_time):
        """Solve using multiprocessing"""
        num_workers = cpu_count
        print(f"Using {num_workers} processes for proof-of-work")
        
        # Shared variables for inter-process communication
        manager = multiprocessing.Manager()
        result_queue = manager.Queue()
        stop_event = manager.Event()
        stats_counter = manager.Value('i', 0)
        
        # Start worker processes
        processes = []
        for i in range(num_workers):
            p = multiprocessing.Process(
                target=pow_worker_function,
                args=(authdata, difficulty, i, result_queue, stop_event, stats_counter, self.valid_chars)
            )
            p.start()
            processes.append(p)
        
        return self._monitor_and_collect_result(start_time, stop_event, stats_counter, result_queue, processes, authdata, difficulty)
    
    def _solve_with_threading(self, authdata, difficulty, num_threads, start_time):
        """Solve using threading"""
        print(f"Using {num_threads} threads for proof-of-work")
        
        # Shared variables for threading
        result_queue = []
        stop_event = threading.Event()
        stats_counter = threading.Lock()
        stats_counter.value = 0
        
        # Start worker threads
        threads = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            for i in range(num_threads):
                future = executor.submit(
                    self.pow_worker_threaded,
                    authdata, difficulty, i, result_queue, stop_event, stats_counter
                )
                threads.append(future)
            
            # Monitor progress
            last_stats_time = start_time
            last_count = 0
            
            while not stop_event.is_set():
                time.sleep(1)
                current_time = time.time()
                current_count = getattr(stats_counter, 'value', 0)
                
                if current_time - last_stats_time >= 10:
                    rate = (current_count - last_count) / (current_time - last_stats_time)
                    elapsed = current_time - start_time
                    print(f"Progress: {current_count:,} hashes in {elapsed:.1f}s (rate: {rate:,.0f} H/s)")
                    last_stats_time = current_time
                    last_count = current_count
                
                if result_queue:
                    break
        
        if result_queue:
            solution, hash_count = result_queue[0]
            elapsed = time.time() - start_time
            rate = hash_count / elapsed if elapsed > 0 else 0
            print(f"Proof-of-work solved in {elapsed:.2f} seconds")
            print(f"Total hashes: {hash_count:,} (rate: {rate:,.0f} H/s)")
            
            # Verify solution
            verification_hash = self.sha1_hash_optimized(authdata + solution)
            target = '0' * int(difficulty)
            if verification_hash.startswith(target):
                print(f"Solution verified: {solution}")
                return solution
            else:
                print(f"Solution verification failed!")
        
        return None
    
    def _monitor_and_collect_result(self, start_time, stop_event, stats_counter, result_queue, processes, authdata, difficulty):
        """Monitor progress and collect results"""
        last_stats_time = start_time
        last_count = 0
        
        try:
            while not stop_event.is_set():
                time.sleep(1)
                current_time = time.time()
                current_count = stats_counter.value
                
                if current_time - last_stats_time >= 10:
                    rate = (current_count - last_count) / (current_time - last_stats_time)
                    elapsed = current_time - start_time
                    print(f"Progress: {current_count:,} hashes in {elapsed:.1f}s (rate: {rate:,.0f} H/s)")
                    last_stats_time = current_time
                    last_count = current_count
                
                if not result_queue.empty():
                    break
        
        except KeyboardInterrupt:
            print("\nStopping workers...")
            stop_event.set()
        
        # Wait for all processes to finish
        for p in processes:
            p.join(timeout=5)
            if p.is_alive():
                p.terminate()
        
        if not result_queue.empty():
            solution, hash_count = result_queue.get()
            elapsed = time.time() - start_time
            rate = hash_count / elapsed if elapsed > 0 else 0
            print(f"Proof-of-work solved in {elapsed:.2f} seconds")
            print(f"Total hashes: {hash_count:,} (rate: {rate:,.0f} H/s)")
            
            # Verify solution
            verification_hash = self.sha1_hash_optimized(authdata + solution)
            target = '0' * int(difficulty)
            if verification_hash.startswith(target):
                print(f"Solution verified: {solution}")
                return solution
            else:
                print(f"Solution verification failed!")
        
        return None
    
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