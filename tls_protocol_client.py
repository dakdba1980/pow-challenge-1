#!/usr/bin/env python3
"""
Ultra-Optimized TLS Protocol Client Implementation
High-performance proof-of-work solver with advanced optimizations
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
import itertools
import queue
from typing import Optional, Tuple

class UltraOptimizedTLSClient:
    def __init__(self, host="18.202.148.130", port=3336, cert_path=None, key_path=None):
        self.host = host
        self.port = port
        self.cert_path = cert_path
        self.key_path = key_path
        self.conn = None
        self.authdata = ""
        
        # Optimized character sets for faster generation
        self.ascii_letters = string.ascii_letters
        self.ascii_digits = string.digits
        self.special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        
        # Combined valid characters (excluding forbidden ones)
        forbidden = set('\n\r\t ')
        all_printable = set(string.printable)
        self.valid_chars = ''.join(sorted(all_printable - forbidden))
        self.valid_chars_list = list(self.valid_chars)
        self.char_count = len(self.valid_chars_list)
        
        # Pre-compute common prefixes for faster string operations
        self.prefix_cache = {}
        
        # Personal information - UPDATE THESE WITH YOUR ACTUAL DETAILS
        self.personal_info = {
            'name': 'Anil Kumar Dasari',
            'emails': ['dak.dba@gmail.com', 'dak.dba@gmail.com'],
            'skype': 'N/A',  # or 'N/A' if no Skype
            'birthdate': '11.07.1980',  # format: %d.%m.%Y
            'country': 'India',
            'address_lines': ['Whitefield', 'Benguluru', 'Karnataka', '560066']
        }
    
    def tls_connect(self):
        """Establish TLS connection with client certificates"""
        try:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            if self.cert_path and self.key_path:
                context.load_cert_chain(self.cert_path, self.key_path)
            
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
    
    def generate_optimized_string(self, length: int, worker_id: int = 0) -> str:
        """Generate optimized random string using worker-specific seeding"""
        # Use worker_id and current time for better distribution
        seed = (worker_id << 32) | int(time.time() * 1000000) % (2**32)
        
        # Fast random generation using secrets but with optimization
        result = []
        for _ in range(length):
            # More efficient character selection
            idx = (seed ^ secrets.randbits(16)) % self.char_count
            result.append(self.valid_chars_list[idx])
            seed = (seed * 1103515245 + 12345) & 0x7fffffff  # Linear congruential generator
        
        return ''.join(result)
    
    def fast_sha1(self, data: str) -> str:
        """Optimized SHA1 computation"""
        return hashlib.sha1(data.encode('utf-8')).hexdigest()
    
    def batch_pow_worker(self, authdata: str, difficulty: int, worker_id: int, 
                        result_queue: queue.Queue, stop_event: threading.Event,
                        batch_size: int = 10000) -> None:
        """Ultra-optimized batch proof-of-work worker"""
        target = '0' * difficulty
        target_len = len(target)
        
        # Pre-compile authdata as bytes for faster hashing
        authdata_bytes = authdata.encode('utf-8')
        
        # Local variables for speed
        sha1 = hashlib.sha1
        valid_chars = self.valid_chars_list
        char_count = self.char_count
        
        # Worker-specific random state
        local_random = secrets.SystemRandom()
        
        iteration = 0
        while not stop_event.is_set():
            # Process in batches for better performance
            for batch in range(batch_size):
                # Generate suffix with varying length (4-12 chars for better distribution)
                suffix_len = 4 + (iteration % 9)
                
                # Fast suffix generation
                suffix = ''.join(valid_chars[local_random.randrange(char_count)] 
                               for _ in range(suffix_len))
                
                # Fast hash computation
                hasher = sha1()
                hasher.update(authdata_bytes)
                hasher.update(suffix.encode('utf-8'))
                cksum = hasher.hexdigest()
                
                # Quick prefix check (faster than startswith for short strings)
                if cksum[:target_len] == target:
                    if not stop_event.is_set():
                        result_queue.put(suffix)
                        stop_event.set()
                    return
                
                iteration += 1
                
                # Early termination check
                if iteration % 1000 == 0 and stop_event.is_set():
                    return
            
            # Brief pause to prevent CPU overload
            if iteration % 100000 == 0:
                time.sleep(0.001)
    
    def parallel_pow_worker(self, args: Tuple[str, int, int, int]) -> Optional[str]:
        """Process-based proof-of-work worker for maximum parallelism"""
        authdata, difficulty, worker_id, max_iterations = args
        
        target = '0' * difficulty
        target_len = len(target)
        authdata_bytes = authdata.encode('utf-8')
        
        # Use different random seeds per process
        local_random = secrets.SystemRandom()
        local_random.seed(worker_id * int(time.time()))
        
        valid_chars = self.valid_chars_list
        char_count = self.char_count
        sha1 = hashlib.sha1
        
        for iteration in range(max_iterations):
            # Variable length suffix (4-16 chars)
            suffix_len = 4 + (iteration % 13)
            
            # Generate suffix
            suffix = ''.join(valid_chars[local_random.randrange(char_count)] 
                           for _ in range(suffix_len))
            
            # Hash computation
            hasher = sha1()
            hasher.update(authdata_bytes)
            hasher.update(suffix.encode('utf-8'))
            cksum = hasher.hexdigest()
            
            # Check solution
            if cksum[:target_len] == target:
                return suffix
        
        return None
    
    def solve_proof_of_work_hybrid(self, authdata: str, difficulty: int) -> Optional[str]:
        """Hybrid proof-of-work solver using both threads and processes"""
        print(f"Solving proof-of-work (difficulty: {difficulty}) with hybrid approach...")
        start_time = time.time()
        
        difficulty_int = int(difficulty)
        
        # Estimate complexity and choose strategy
        if difficulty_int <= 5:
            # Use thread-based approach for lower difficulty
            return self.solve_proof_of_work_threaded(authdata, difficulty_int)
        else:
            # Use process-based approach for higher difficulty
            return self.solve_proof_of_work_multiprocess(authdata, difficulty_int)
    
    def solve_proof_of_work_threaded(self, authdata: str, difficulty: int) -> Optional[str]:
        """Thread-based proof-of-work solver"""
        # Use more threads for better parallelism
        cpu_count = multiprocessing.cpu_count()
        num_threads = min(cpu_count * 2, 32)  # Up to 32 threads
        
        result_queue = queue.Queue()
        stop_event = threading.Event()
        
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(
                target=self.batch_pow_worker,
                args=(authdata, difficulty, i, result_queue, stop_event, 50000)
            )
            thread.daemon = True
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for result with timeout
        timeout = 14400  # 4 hour timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                result = result_queue.get(timeout=1)
                stop_event.set()
                
                # Wait for threads to finish
                for thread in threads:
                    thread.join(timeout=1)
                
                elapsed = time.time() - start_time
                print(f"Proof-of-work solved in {elapsed:.2f} seconds (threaded)")
                return result
                
            except queue.Empty:
                if stop_event.is_set():
                    break
                continue
        
        stop_event.set()
        print("Proof-of-work timeout (threaded)")
        return None
    
    def solve_proof_of_work_multiprocess(self, authdata: str, difficulty: int) -> Optional[str]:
        """Process-based proof-of-work solver for maximum performance"""
        cpu_count = multiprocessing.cpu_count()
        num_processes = cpu_count
        print(f"Using {num_processes} processes for proof-of-work")
        
        # Distribute work among processes
        iterations_per_process = 1000000  # 1M iterations per process
        print(f"Using {iterations_per_process} iterations per process for proof-of-work")
        
        # Create process pool
        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            # Submit tasks
            futures = []
            for i in range(num_processes):
                args = (authdata, difficulty, i, iterations_per_process)
                future = executor.submit(self.parallel_pow_worker, args)
                futures.append(future)
            
            # Wait for first result
            start_time = time.time()
            timeout = 14400  # 4 hour timeout
            
            try:
                for future in as_completed(futures, timeout=timeout):
                    result = future.result()
                    if result:
                        # Cancel remaining tasks
                        for f in futures:
                            f.cancel()
                        
                        elapsed = time.time() - start_time
                        print(f"Proof-of-work solved in {elapsed:.2f} seconds (multiprocess)")
                        return result
                
            except Exception as e:
                print(f"Process execution error: {e}")
        
        print("Proof-of-work timeout (multiprocess)")
        return None
    
    def solve_proof_of_work(self, authdata: str, difficulty: str) -> Optional[str]:
        """Main proof-of-work solver with adaptive strategy"""
        try:
            difficulty_int = int(difficulty)
            
            # Choose optimal strategy based on difficulty
            if difficulty_int <= 3:
                # Very low difficulty - use simple approach
                return self.solve_proof_of_work_simple(authdata, difficulty_int)
            elif difficulty_int <= 5:
                # Medium difficulty - use threaded approach
                return self.solve_proof_of_work_threaded(authdata, difficulty_int)
            else:
                # High difficulty - use multiprocess approach
                return self.solve_proof_of_work_multiprocess(authdata, difficulty_int)
                
        except ValueError:
            print(f"Invalid difficulty value: {difficulty}")
            return None
    
    def solve_proof_of_work_simple(self, authdata: str, difficulty: int) -> Optional[str]:
        """Simple proof-of-work solver for very low difficulty"""
        target = '0' * difficulty
        target_len = len(target)
        authdata_bytes = authdata.encode('utf-8')
        
        sha1 = hashlib.sha1
        valid_chars = self.valid_chars_list
        char_count = self.char_count
        
        for iteration in range(1000000):  # 1M iterations max
            # Generate suffix
            suffix_len = 4 + (iteration % 8)
            suffix = ''.join(valid_chars[secrets.randbelow(char_count)] 
                           for _ in range(suffix_len))
            
            # Hash and check
            hasher = sha1()
            hasher.update(authdata_bytes)
            hasher.update(suffix.encode('utf-8'))
            cksum = hasher.hexdigest()
            
            if cksum[:target_len] == target:
                print(f"Proof-of-work solved in {iteration + 1} iterations (simple)")
                return suffix
        
        print("Proof-of-work timeout (simple)")
        return None
    
    def create_authenticated_response(self, nonce, data):
        """Create authenticated response with SHA1 hash"""
        return self.fast_sha1(self.authdata + nonce) + " " + data
    
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
            print(f"Starting proof-of-work with difficulty {difficulty}")
            
            solution = self.solve_proof_of_work(self.authdata, difficulty)
            if solution:
                print(f"Found solution: {solution[:20]}...")
                return self.write_line(solution)
            else:
                print("Failed to solve proof-of-work within time limit")
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
                line = self.read_line()
                if not line:
                    print("Connection closed by server")
                    break
                
                print(f"Received: {line}")
                args = line.split(' ')
                
                if not self.handle_command(args):
                    break
                
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

# Alias for backward compatibility
OptimizedTLSClient = UltraOptimizedTLSClient

def main():
    """Main function with command line argument support"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ultra-Optimized TLS Protocol Client')
    parser.add_argument('--host', default='18.202.148.130', help='Server hostname')
    parser.add_argument('--port', type=int, default=3336, help='Server port')
    parser.add_argument('--cert', help='Client certificate file path')
    parser.add_argument('--key', help='Client private key file path')
    parser.add_argument('--benchmark', action='store_true', help='Run proof-of-work benchmark')
    
    args = parser.parse_args()
    
    # Benchmark mode
    if args.benchmark:
        print("Running proof-of-work benchmark...")
        client = UltraOptimizedTLSClient()
        
        for difficulty in range(1, 7):
            print(f"\nTesting difficulty {difficulty}...")
            start_time = time.time()
            
            solution = client.solve_proof_of_work("benchmark", str(difficulty))
            if solution:
                elapsed = time.time() - start_time
                print(f"Difficulty {difficulty}: {elapsed:.2f} seconds")
            else:
                print(f"Difficulty {difficulty}: TIMEOUT")
        
        return
    
    # Normal client mode
    client = UltraOptimizedTLSClient(
        host=args.host,
        port=args.port,
        cert_path=args.cert,
        key_path=args.key
    )
    
    print("=== Ultra-Optimized TLS Protocol Client ===")
    print(f"Connecting to {args.host}:{args.port}")
    print(f"CPU cores available: {multiprocessing.cpu_count()}")
    
    if client.run():
        print("Client completed successfully")
        sys.exit(0)
    else:
        print("Client failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
