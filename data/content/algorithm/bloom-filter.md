---
track: algorithm
difficulty: Easy
algorithms: bloom-filter
category: Data Structure
source: authored
io_mode: function
---
# Bloom filter — Easy — Data Structure

A Bloom filter is a bit array of m bits with k hash functions. Insert sets k bits; a query reports "definitely absent" if any of the k bits is 0, else "probably present". It never gives false negatives and cannot delete (a counting Bloom filter can). False-positive rate ≈ (1 − e^(−kn/m))^k for n inserted items; the optimal k = (m/n)·ln 2. At 10 bits per element with k = 7 the rate is about 0.8%. Databases such as RocksDB and Cassandra use it to skip disk reads for missing keys.
