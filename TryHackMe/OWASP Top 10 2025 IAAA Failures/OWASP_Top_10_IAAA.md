# TryHackMe — OWASP Top 10 2025: IAAA Failures

| Field          | Details                                                                                          |
|----------------|--------------------------------------------------------------------------------------------------|
| **Platform**   | TryHackMe                                                                                        |
| **Room**       | [OWASP Top 10 2025: IAAA Failures](https://tryhackme.com/room/owasptopten2025one)               |
| **Difficulty** | Easy                                                                                             |
| **Type**       | Web Application Security                                                                         |
| **Category**   | OWASP Top 10, Access Control, Authentication, Logging                                            |
| **Tags**       | IDOR, Broken Access Control, Authentication Failures, Logging, OWASP                            |
| **Completed**  | June 2026                                                                                        |

---

## Overview

This room covers three entries from the OWASP Top 10 2025 through the lens of the **IAAA model** — a framework for thinking about how user identity and actions are verified in web applications. The three vulnerabilities covered are:

- **A01 — Broken Access Control** (IDOR)
- **A07 — Authentication Failures**
- **A09 — Logging & Alerting Failures**

---

## The IAAA Model

IAAA is a layered model — each layer depends on the one before it. If a previous layer is broken, everything after it collapses.

| Layer              | What it means                                                        |
|--------------------|----------------------------------------------------------------------|
| **Identity**       | The unique account (user ID, email) that represents a person or service |
| **Authentication** | Proving that identity — passwords, OTP, passkeys                     |
| **Authorisation**  | What that verified identity is allowed to do                         |
| **Accountability** | Recording and alerting on who did what, when, and from where         |

> If Authentication is broken, Authorisation and Accountability become meaningless — you can't control or audit what an unverified user does.

---

## Task 1 — A01: Broken Access Control (IDOR)

### Concept

Broken Access Control happens when the server doesn't properly enforce who can access what **on every request**. The most common form is **IDOR (Insecure Direct Object Reference)** — where changing a parameter in the URL (like `?id=7` → `?id=6`) gives you access to another user's data.

**Two types of privilege escalation that result:**

| Type                        | What it means                                  |
|-----------------------------|------------------------------------------------|
| Horizontal privilege escalation | Same role, accessing another user's data   |
| Vertical privilege escalation   | Jumping to a higher role (e.g., admin)     |

### Challenge

> Find the note on the account with more than $1 million.

### Approach

Launched the static site attached to the task. Identified that the URL contained an `accountID` parameter. By manipulating the ID value in the URL, I was able to access other users' accounts without authentication — a textbook IDOR vulnerability.

### Flag

>  `THM{Found.the.Millionare!}`

---

## Task 2 — A07: Authentication Failures

### Concept

Authentication Failures occur when an application cannot reliably verify or bind a user's identity. Common weaknesses include:

- Username enumeration through different error messages
- Weak or guessable passwords with no lockout or rate limiting
- Logic flaws in the login or registration flow
- Insecure session or cookie handling

If any of these exist, an attacker can log in as another user or bind a session to the wrong account.

### Challenge

> Find the flag on the admin user's dashboard.

### Approach

Launched the static site. Registered a new account, then exploited an **account confusion vulnerability** in the authentication flow to gain access to the admin user's dashboard without knowing the admin password.

### Flag

>  `THM{Account.Confusion.FTW!}`

---

## Task 3 — A09: Logging & Alerting Failures

### Concept

When applications don't record or alert on security-relevant events, defenders lose the ability to detect or investigate attacks. Logging is what makes **Accountability** (the A in IAAA) possible.

**Common failures:**

- Missing authentication events (failed logins not recorded)
- Vague or incomplete error logs
- No alerting on brute-force attempts or privilege changes
- Short log retention periods
- Logs stored on the same host — attackers can tamper with them

### Challenge

Investigate the log file to identify a brute-force attack:
- Who performed the attack (IP address)
- Which account was targeted
- Whether access was gained
- What action was performed using that account

### Approach

Launched the static site and analysed the provided log file. Traced the sequence of failed login attempts to identify the attacker's IP, the targeted account, the successful login event, and the subsequent malicious action performed under that account.

---

## Key Lessons Learned

1. **IDOR is still one of the most common web vulnerabilities.** Never trust client-supplied IDs without server-side authorisation checks on every single request. Changing `?id=6` to `?id=7` should never return another user's data.

2. **Access control must be enforced server-side, not just hidden in the UI.** Hiding a button in the frontend is not access control. The server must validate permissions on every API call independently.

3. **Authentication logic flaws are easy to miss and devastating to exploit.** Account confusion bugs often come from poor session handling or registration flow edge cases — not just weak passwords.

4. **Logging is a security control, not just an ops tool.** Without logs, you cannot detect an attack, investigate an incident, or hold anyone accountable. The IAAA model breaks at the final layer without it.

5. **Logs must be tamper-proof and off-host.** Storing logs on the same machine the attacker compromised is useless — they can simply delete them. Centralised, off-host log storage is a must.

6. **The IAAA model shows why order matters.** If Authentication (A2) is broken, Authorisation (A3) is bypassed and Accountability (A4) is meaningless — you cannot audit actions you cannot attribute to a verified identity.

---

## Summary Table

| OWASP ID | Vulnerability              | Root Cause                                      | Fix                                                |
|----------|----------------------------|-------------------------------------------------|----------------------------------------------------|
| A01      | Broken Access Control      | No server-side check on object ownership        | Validate ownership on every request server-side    |
| A07      | Authentication Failures    | Logic flaw in auth/session flow                 | Enforce unique identity binding, rate limiting     |
| A09      | Logging & Alerting Failures| Security events not recorded or alerted         | Log full auth lifecycle, centralise, set alerts    |

---

## References

- [TryHackMe — OWASP Top 10 2025: IAAA Failures](https://tryhackme.com/room/owasptopten2025one)
- [OWASP Top 10 2021 — A01 Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- [OWASP Top 10 2021 — A07 Identification and Authentication Failures](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/)
- [OWASP Top 10 2021 — A09 Security Logging and Monitoring Failures](https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/)