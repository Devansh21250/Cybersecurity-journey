# TryHackMe - Hidden Deep Into My Heart

| Field | Details |
| --- | --- |
| **Platform** | TryHackMe |
| **Room** | [Hidden Deep Into My Heart](https://tryhackme.com/room/lafb2026e9) |
| **Difficulty** | Easy |
| **Category** | Security Misconfiguration, Supply Chain, Cryptography, Insecure Design |
| **Tags** | OWASP Top 10 2025, Verbose Errors, Supply Chain, AES-ECB, API Security, Insecure Design |
| **Completed** | September 2026 |

---

## Overview

Cupid's Vault was designed to safeguard secrets meant to stay hidden forever. Unfortunately, Cupid underestimated how determined attackers can be.

Intelligence suggested that Cupid had unintentionally introduced vulnerabilities into the system. With a holiday deadline looming, the objective was to uncover what was hidden inside the vault before it was too late.

The target application was accessible at:

```
http://MACHINE_IP:5000
```

---

## Task 1 — Deep Into My Heart

### Objective

Find the flag hidden within the web application.

### Methodology

**1. Reconnaissance**

Scanned the target to confirm the web service was live and identify the exposed port:

```bash
nmap -p 5000 -sV MACHINE_IP
```

This confirmed a web application running on port 5000.

**2. Initial Enumeration**

Ran a directory brute-force against the web root to discover hidden files and endpoints:

```bash
gobuster dir -u http://MACHINE_IP:5000 -w /usr/share/wordlists/dirb/common.txt
```

This uncovered two notable paths:

- `/console`
- `/robots.txt`

**3. robots.txt Disclosure**

Navigating to `robots.txt` revealed a disallowed path not linked anywhere else on the site:

```
/cupids_secret_vault/
```

Visiting this path returned a message hinting that there was "more to discover," suggesting further hidden content beneath it.

**4. Secondary Enumeration**

Ran a second directory scan scoped to the newly discovered path:

```bash
gobuster dir -u http://MACHINE_IP:5000/cupids_secret_vault/ -w /usr/share/wordlists/dirb/common.txt
```

This revealed an `/administrator` endpoint, which led to a login form ("Cupid's Vault") requiring a username and password.

**5. Credential Discovery**

Initial attempts with common/default credentials against the login form were unsuccessful, each returning an "Invalid credentials!" error.

Retracing earlier enumeration steps and re-examining `robots.txt` more closely revealed that the file also contained a plaintext password, which had been overlooked during the initial pass.

**6. Authentication**

Using the disclosed password together with the username `admin`, authentication to the `/administrator` panel succeeded, revealing the flag.

### Flag

```
THM{l0v3_is_in_th3_r0b0ts_txt}
```

---

## Key Lessons Learned

- **Sensitive data in `robots.txt`**: This file is intended to guide web crawlers, not to store secrets. Anything placed in it is publicly readable by anyone, crawler or not, and should never contain credentials, paths to sensitive functionality, or other confidential information.
- **Verbose error messages**: The generic "Invalid credentials!" message was consistent regardless of whether the username or password was wrong, which is good practice — but it's still worth noting that any distinguishing behavior between "unknown user" and "wrong password" would have made credential enumeration easier for an attacker.
- **Re-checking earlier recon output pays off**: The password was hiding in data already collected early in the engagement (`robots.txt`). This is a good reminder that thorough re-review of previously gathered information is often more productive than moving straight to brute-forcing.
- **Defense-in-depth**: Relying on an unlinked, "hidden" directory as a form of protection (security through obscurity) is not a substitute for proper authentication and access controls.

---

## References

- [TryHackMe Room: Hidden Deep Into My Heart](https://tryhackme.com/room/lafb2026e9)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)