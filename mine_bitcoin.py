import hashlib
import time
import multiprocessing

def mine_range(start, step, block_number, transactions, previous_hash, difficulty, stop_event, result_queue):
    """
    Search for a valid nonce in a given range.
    Each worker starts at a different nonce and increments by 'step'.
    """
    prefix_str = '0' * difficulty
    nonce = start
    while not stop_event.is_set():
        # Create the data string from block information and nonce
        data = f"{block_number}{transactions}{previous_hash}{nonce}"
        new_hash = hashlib.sha256(data.encode()).hexdigest()
        if new_hash.startswith(prefix_str):
            # If a valid hash is found, put the result in the queue and signal to stop
            result_queue.put((new_hash, nonce))
            stop_event.set()
            return
        nonce += step

def parallel_mine(block_number, transactions, previous_hash, difficulty, num_processes):
    """
    Launch multiple processes to search for a valid nonce in parallel.
    """
    manager = multiprocessing.Manager()
    stop_event = manager.Event()
    result_queue = manager.Queue()

    processes = []
    for i in range(num_processes):
        p = multiprocessing.Process(
            target=mine_range,
            args=(i, num_processes, block_number, transactions, previous_hash, difficulty, stop_event, result_queue)
        )
        processes.append(p)
        p.start()

    # Wait until one of the processes puts a result in the queue
    result = result_queue.get()

    # Terminate all processes (they will exit shortly anyway because stop_event is set)
    for p in processes:
        p.terminate()

    return result

if __name__ == '__main__':
    # Example block data (for demonstration purposes only)
    block_number = 1
    transactions = "Alice pays Bob 0.5 BTC; Charlie pays Dave 1.2 BTC"
    previous_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    
    # Set a difficulty (number of leading zeros required in the hash)
    difficulty = 5  # Increase for a harder puzzle
    # Use all available CPU cores
    num_processes = multiprocessing.cpu_count()
    
    print(f"Starting mining with {num_processes} processes and difficulty {difficulty}...")
    start_time = time.time()
    
    found_hash, nonce = parallel_mine(block_number, transactions, previous_hash, difficulty, num_processes)
    
    end_time = time.time()
    print("Block mined!")
    print(f"Hash: {found_hash}")
    print(f"Nonce: {nonce}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
