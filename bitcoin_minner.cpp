#include <iostream>
#include <sstream>
#include <iomanip>
#include <string>
#include <thread>
#include <atomic>
#include <vector>
#include <chrono>
#include <mutex>
#include <openssl/sha.h>

// Global variables to store the result
std::atomic<bool> solutionFound(false);
std::string globalHash;
long globalNonce = 0;
std::mutex resultMutex;

// Function to compute SHA256 hash of a given string
std::string computeSHA256(const std::string &data) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(data.c_str()), data.size(), hash);

    std::stringstream ss;
    for (int i = 0; i < SHA256_DIGEST_LENGTH; ++i) {
        ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(hash[i]);
    }
    return ss.str();
}

// Worker function: each thread will try different nonces in steps
void mineWorker(int start, int step, int blockNumber, 
                const std::string &transactions, 
                const std::string &previousHash, 
                int difficulty) {
    // The target is a hash that starts with 'difficulty' number of zeros.
    std::string targetPrefix(difficulty, '0');
    long nonce = start;
    while (!solutionFound.load()) {
        // Combine block data with the nonce
        std::stringstream ss;
        ss << blockNumber << transactions << previousHash << nonce;
        std::string data = ss.str();
        
        // Compute the SHA256 hash
        std::string hashStr = computeSHA256(data);
        
        // Check if the hash meets the difficulty requirement
        if (hashStr.substr(0, difficulty) == targetPrefix) {
            // If a valid nonce is found, store the result
            if (!solutionFound.exchange(true)) { // only one thread wins
                std::lock_guard<std::mutex> lock(resultMutex);
                globalHash = hashStr;
                globalNonce = nonce;
            }
            break;
        }
        nonce += step;
    }
}

int main() {
    // Example block data (for demonstration purposes)
    int blockNumber = 1;
    std::string transactions = "Alice pays Bob 0.5 BTC; Charlie pays Dave 1.2 BTC";
    std::string previousHash = "0000000000000000000000000000000000000000000000000000000000000000";
    
    // Set difficulty (number of leading zeros required in the hash)
    // Note: Higher difficulty means longer runtime. For testing, use a small value.
    int difficulty = 5;

    // Determine the number of threads to run (using available CPU cores)
    unsigned int numThreads = std::thread::hardware_concurrency();
    if (numThreads == 0) numThreads = 4; // fallback if hardware_concurrency returns 0

    std::cout << "Starting mining with " << numThreads << " threads and difficulty " << difficulty << "...\n";
    auto startTime = std::chrono::steady_clock::now();

    // Create and launch threads
    std::vector<std::thread> threads;
    for (unsigned int i = 0; i < numThreads; ++i) {
        threads.emplace_back(mineWorker, i, numThreads, blockNumber, transactions, previousHash, difficulty);
    }

    // Wait for all threads to finish
    for (auto &th : threads) {
        if (th.joinable())
            th.join();
    }

    auto endTime = std::chrono::steady_clock::now();
    std::chrono::duration<double> elapsed = endTime - startTime;

    // Print the results
    if (solutionFound.load()) {
        std::cout << "Block mined!\n";
        std::cout << "Hash: " << globalHash << "\n";
        std::cout << "Nonce: " << globalNonce << "\n";
        std::cout << "Time taken: " << elapsed.count() << " seconds\n";
    } else {
        std::cout << "No valid nonce found.\n";
    }

    return 0;
}
