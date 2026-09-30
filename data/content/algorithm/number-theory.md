---
track: algorithm
difficulty: Medium
algorithms: number-theory
category: Algorithm
source: authored
io_mode: function
---
# Number theory essentials — Medium — Algorithm

- **GCD and LCM:** Euclid's algorithm replaces (a, b) with (b, a mod b) until b = 0. LCM = a ÷ gcd(a, b) × b (divide first to avoid overflow).
- **Fast modular exponentiation:** square the base and halve the exponent each step, multiplying the result in when the low bit is 1.
- **Sieve of Eratosthenes:** mark multiples of each prime from p² upward; all primes up to n in O(n log log n).
- **Modular inverse:** for prime p, a⁻¹ ≡ a^(p−2) mod p (Fermat); for general moduli use the extended Euclidean algorithm.
- **Combinations mod p:** precompute factorials and inverse factorials for O(1) queries, or multiply and invert once per query.
- **Common modulus:** 10⁹ + 7 is prime, and the product of two residues fits in a signed 64-bit integer.
- **Primality:** trial division up to √n for single checks; Miller–Rabin for 64-bit values.

#### Number theory helpers — Python

```python
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def mod_pow(base, exp, mod):
    result, base = 1, base % mod
    while exp:
        if exp & 1:
            result = result * base % mod
        base = base * base % mod
        exp >>= 1
    return result

def sieve(n):
    is_prime = bytearray([1]) * (n + 1)
    is_prime[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if is_prime[i]:
            is_prime[i * i::i] = bytearray(len(is_prime[i * i::i]))
    return [i for i in range(n + 1) if is_prime[i]]

def ncr_mod(n, r, p=10**9 + 7):
    num = den = 1
    for i in range(r):
        num = num * (n - i) % p
        den = den * (i + 1) % p
    return num * pow(den, p - 2, p) % p       # Fermat inverse of den
```
