# TryHackMe - W1seGuy

| Field | Details |
| --- | --- |
| **Platform** | TryHackMe |
| **Room** | [https://tryhackme.com/room/w1seguy](https://tryhackme.com/room/w1seguy) |
| **Difficulty** | Easy |
| **Category** | Cryptography, Insecure Design |
| **Tags** | XOR, Known-Plaintext Attack, Weak Key Generation |
| **Completed** | September 2026 |

---

## Overview

Download and review the Source Code given.

“Your friend told me you were wise, but I don't believe them. Can you prove me wrong?

When you are ready, click the Start Lab Machine button to fire up the Lab Machine. Please allow 3-5 minutes for the VM to start fully.

The server is listening on port 1337 via TCP. You can connect to it using Netcat or any other tool you prefer.”

The target service was accessible via:

```
nc MACHINE_IP 1337
```

---

## Task - Get the flags

### Objective

Recover the encryption key used by a remote service in order to obtain the second, genuine flag.

### Approach

1. Connected to the remote service over TCP on port `1337`. On connection, the server returned a hex-encoded ciphertext labeled "flag 1," followed by a prompt asking for the encryption key that had been used to produce it.
2. The ciphertext was determined to be the result of a **repeating-key XOR** cipher - a scheme where a short key is repeated across the length of the message and combined byte-by-byte with the plaintext using the XOR operation.
3. Since TryHackMe flags follow a predictable format (`THM{...}`), the first few characters of the plaintext could be assumed in advance. XOR-ing these known plaintext bytes against the corresponding ciphertext bytes recovered the corresponding bytes of the encryption key directly.

Because the key was short and only a portion of it could be recovered this way, the remaining unknown character(s) were determined by testing the limited set of valid candidates (alphanumeric characters) and checking which one produced a fully valid, readable flag.

Once the full key was reconstructed, it was submitted back to the service when prompted. The server validated the key and returned the second, genuine flag.

### Flags

```
Flag 1: THM{p1alntExtAtt4ckcAnr3alLyhUrty0urxOr}
Flag 2: THM{BrUt3_ForC1nG_XOR_cAn_B3_FuN_nO?}
```

---

## Key Lessons Learned

- Repeating-key XOR is weak against known-plaintext attacks.
- Short keys are brute-forceable once partially known.

---

## References

- [https://tryhackme.com/room/w1seguy](https://tryhackme.com/room/w1seguy)
- [Wikipedia: XOR Cipher](https://en.wikipedia.org/wiki/XOR_cipher)
- [Wikipedia: Known-Plaintext Attack](https://en.wikipedia.org/wiki/Known-plaintext_attack)