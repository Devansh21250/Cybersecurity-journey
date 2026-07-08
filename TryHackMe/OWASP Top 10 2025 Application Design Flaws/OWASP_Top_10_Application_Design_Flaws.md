# TryHackMe — OWASP Top 10 2025: Application Design Flaws

| Field          | Details                                                                                                      |
|----------------|--------------------------------------------------------------------------------------------------------------|
| **Platform**   | TryHackMe                                                                                                    |
| **Room**       | [OWASP Top 10 2025: Application Design Flaws](https://tryhackme.com/room/owasptopten2025two)                 |
| **Difficulty** | Easy                                                                                                         |
| **Type**       | Web Application Security                                                                                     |
| **Category**   | Security Misconfiguration, Supply Chain, Cryptography, Insecure Design                                       |
| **Tags**       | OWASP Top 10 2025, Verbose Errors, Supply Chain, AES-ECB, API Security, Insecure Design                     |
| **Completed**  | June 2026                                                                                                    |

---

## Overview

This room covers four OWASP Top 10 2025 categories through hands-on web application challenges. Each task exposes a real-world design flaw and requires actively exploiting it to retrieve a flag.

**Vulnerabilities covered:**
- **A02 — Security Misconfigurations** (verbose error leakage)
- **A03 — Software Supply Chain Failures** (vulnerable dependency exploitation)
- **A04 — Cryptographic Failures** (hardcoded key, weak AES-ECB cipher)
- **A06 — Insecure Design** (unauthenticated API assumption)

---

## Task 1 — A02: Security Misconfigurations

### Concept

Security misconfigurations occur when systems are deployed with unsafe defaults, unnecessary services exposed, or verbose error messages that leak internal details to attackers. Even a single misconfiguration can provide a foothold into an otherwise secure system.

**Common patterns:**
- Default or weak credentials left unchanged
- Unnecessary services or endpoints exposed to the internet
- Verbose error messages exposing stack traces or system details
- Misconfigured cloud storage permissions (S3, Azure Blob, GCP buckets)
- Outdated software or containers with known vulnerabilities

### Challenge

> Navigate to `MACHINE_IP:5002`. The developers left too many traces in their User Management API. Find the flag.

### Approach

Navigated to `MACHINE_IP:5002` — the API documentation indicated that `GET /api/users/{id}` accepts a numeric user ID. Tested several numeric values:

```
GET http://MACHINE_IP:5002/api/users/123
GET http://MACHINE_IP:5002/api/users/1
GET http://MACHINE_IP:5002/api/users/456
```

Each returned user data (id, name, password) but no flag. The API documentation also stated the ID must be numeric. Tested with a non-numeric value to trigger an error response:

```
GET http://MACHINE_IP:5002/api/users/abc
```

The verbose error response leaked internal system information — including the flag.

**Key insight:** The application was configured to expose detailed error messages in production. This is a classic Security Misconfiguration — error handling should never reveal internal details to the end user.

### Flag

>  `THM{V3RB0S3_3RR0R_L34K}`

---

## Task 2 — A03: Software Supply Chain Failures

### Concept

Software supply chain failures occur when applications rely on third-party components, libraries, or services that are compromised, outdated, or unverified. A single vulnerable dependency can compromise an entire system — without the attacker ever touching the application's own code.

**Common patterns:**
- Using unverified or unmaintained libraries
- Auto-installing updates without integrity checks
- Insecure CI/CD pipelines that allow build tampering
- No monitoring for newly disclosed vulnerabilities in dependencies

### Challenge

> Navigate to `MACHINE_IP:5003`. The code imports an old `lib/vulnerable_utils.py` component. Debug it to find the flag.

### Approach

Downloaded the Python source file attached to the task and reviewed the vulnerable dependency. Found that the library contains a debug mode triggered by a specific input value:

```python
if data == "debug":
    return debug_info  # leaks internal flag
```

Exploited this by sending a POST request with `"debug"` as the data value:

```bash
curl -X POST http://MACHINE_IP:5003/api/process \
  -H "Content-Type: application/json" \
  -d '{"data": "debug"}'
```

The response returned the internal debug information including the flag.

**Key insight:** The vulnerable third-party library had a debug backdoor that was never removed before production deployment. This is why dependency auditing and code review of third-party components is critical.

### Flag

>  `THM{SUPPLY_CH41N_VULN3R4B1L1TY}`

---

## Task 3 — A04: Cryptographic Failures

### Concept

Cryptographic failures occur when encryption is used incorrectly or not at all — weak algorithms, hardcoded keys, poor key management, or unencrypted sensitive data in transit or at rest.

**Common patterns:**
- Deprecated or weak algorithms: MD5, SHA-1, AES in ECB mode
- Hardcoded secrets in source code or configuration files
- No TLS or use of self-signed/invalid certificates
- Poor key rotation practices

### Challenge

> Navigate to `MACHINE_IP:5004`. Find the key to decrypt the file and retrieve the flag.

### Approach

Navigated to `MACHINE_IP:5004` — the page presented an encrypted document. Viewed the page source and found a reference to a JavaScript file:

```
/static/js/decrypt.js
```

Opened the file and found the encryption details hardcoded directly in the client-side JavaScript:

```javascript
// Encryption mode: AES-ECB
// Secret key: my-secret-key-16
```

Two critical flaws identified:
1. **Hardcoded key** — the encryption key was embedded in publicly accessible JavaScript
2. **Weak cipher mode** — AES in ECB (Electronic Codebook) mode is deterministic and does not hide patterns in plaintext

Used CyberChef to decrypt the document:
- Operation: `AES Decrypt`
- Mode: `ECB`
- Key: `my-secret-key-16`

Decryption revealed the flag.

**Key insight:** Hardcoding secrets in client-side code is equivalent to no encryption at all — anyone can view page source. AES-ECB should never be used for sensitive data as it produces identical ciphertext for identical plaintext blocks, leaking data patterns.

### Flag

>  `THM{CRYPTO_FAILURE_H4RDCOD3D_K3Y}`

---

## Task 4 — A06: Insecure Design

### Concept

Insecure design occurs when flawed logic or assumptions are built into a system from the start — not implementation bugs, but fundamental architectural mistakes. A common example is assuming that only authorised clients (like a mobile app) will ever access a backend API, without enforcing actual authentication.

**Common patterns:**
- Weak business logic in recovery or approval flows
- APIs accessible without authentication because "only the app will call them"
- Test or debug bypasses left in production
- AI components with unchecked authority or access
- No abuse-case review during design

### Challenge

> Navigate to `MACHINE_IP:5005`. Have they assumed only mobile devices can access it?

### Approach

Navigated to `MACHINE_IP:5005` — a secure messaging web app. The challenge hint referenced the Clubhouse API incident, where backend APIs had no authentication because the design assumed only the mobile app would access them.

**Step 1 — Identify the API base path:**

Based on the Clubhouse example in the room, tried `/api` as the base endpoint:

```
GET http://MACHINE_IP:5005/api
```

This returned a valid response, confirming an unauthenticated API exists.

**Step 2 — Enumerate users:**

```
GET http://MACHINE_IP:5005/api/users
```

Found three users: `admin`, `alice`, `bob`.

**Step 3 — Find the messages endpoint:**

Tried several URL patterns:
```
GET http://MACHINE_IP:5005/api/users/messages  → 404
GET http://MACHINE_IP:5005/api/messages        → 404
GET http://MACHINE_IP:5005/api/messages/users  → error: user not found
```

The last response confirmed the correct endpoint structure — just needed a valid username appended:

```
GET http://MACHINE_IP:5005/api/messages/admin
```

Returned the admin's private messages including the flag.

**Key insight:** The application assumed only the mobile frontend would call the API, so no authentication was implemented on the backend. Any user who knows (or guesses) the API structure has full access. This is not an implementation bug — it is a design failure.

### Flag

>  `THM{1NS3CUR3_D35IGN_4SSUMPT10N}`

---

## Summary Table

| OWASP ID | Vulnerability                    | Root Cause                                      | Fix                                                         |
|----------|----------------------------------|-------------------------------------------------|-------------------------------------------------------------|
| A02      | Security Misconfiguration        | Verbose errors exposing internal details        | Suppress error details in production, use generic messages  |
| A03      | Software Supply Chain Failure    | Vulnerable dependency with debug backdoor       | Audit dependencies, remove debug code before deployment     |
| A04      | Cryptographic Failure            | Hardcoded key + weak AES-ECB cipher             | Use key management services, switch to AES-GCM or ChaCha20 |
| A06      | Insecure Design                  | API assumed only mobile clients would access it | Enforce authentication on every API endpoint, always        |

---

## Key Lessons Learned

1. **Verbose errors are an attacker's best friend.** A "user not found" vs "invalid input" distinction alone can help enumerate valid accounts. Production systems must suppress all internal details from error responses.

2. **Dependencies are part of your attack surface.** You are responsible for every library you import. A debug backdoor in a third-party component is your vulnerability once you ship it.

3. **Client-side code is public.** Anything in JavaScript — keys, endpoints, logic — is readable by anyone with a browser. Never put secrets there. An AES key in `decrypt.js` is the same as no encryption.

4. **AES-ECB is not safe encryption.** ECB mode encrypts each block independently, so identical plaintext blocks produce identical ciphertext. This leaks patterns and makes the encryption trivially breakable.

5. **"Only our app will call this" is not security.** APIs must authenticate every caller, regardless of which client is expected to use them. Assumptions about who will access a system are not access controls.

6. **Insecure design cannot be patched — it must be redesigned.** The difference between a bug and a design flaw is that bugs can be fixed with a patch. Design flaws like missing API authentication require rethinking the architecture entirely.

---

## References

- [TryHackMe — OWASP Top 10 2025: Application Design Flaws](https://tryhackme.com/room/owasptopten2025two)
- [OWASP A02 — Security Misconfiguration](https://owasp.org/Top10/A05_2021-Security_Misconfiguration/)
- [OWASP A03 — Software and Data Integrity Failures](https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/)
- [OWASP A04 — Cryptographic Failures](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)
- [OWASP A06 — Insecure Design](https://owasp.org/Top10/A04_2021-Insecure_Design/)
- [CyberChef](https://gchq.github.io/CyberChef/)