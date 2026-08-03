import re
from collections import Counter

def analyze_attempts(attempts):
    # Count per IP
    ip_counts = Counter(a['ip'] for a in attempts)
    
    # Count per user
    user_counts = Counter(a['user'] for a in attempts)
    
    # Flag brute force (threshold: 5 attempts)
    brute_force_ips = {}
    for ip, count in ip_counts.items():
        if count > 5:
            brute_force_ips[ip] = count
    
    return {
        'total_failed': len(attempts),
        'unique_ips': len(ip_counts),
        'brute_force_ips': brute_force_ips,
        'all_ips': dict(ip_counts)
    }


def parse_ssh_log(filename):
    failed_attempts = []
    
    with open(filename, 'r') as file:
        for line in file:
            # Check if this line is a failed login
            if 'Failed password' in line:
                # Extract IP address using regex
                ip_match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', line)
                # Extract username
                user_match = re.search(r'for (\w+)', line)
                
                if ip_match and user_match:
                    attempt = {
                        'ip': ip_match.group(1),
                        'user': user_match.group(1),
                        'line': line.strip()
                    }
                    failed_attempts.append(attempt)
    
    return failed_attempts

# Test it
results = parse_ssh_log('sample_auth.log')
analysis = analyze_attempts(results)

print(f"\n=== ANALYSIS ===")
print(f"Total failed attempts: {analysis['total_failed']}")
print(f"Unique IPs: {analysis['unique_ips']}")

if analysis['brute_force_ips']:
    print(f"\nBRUTE FORCE DETECTED:")
    for ip, count in analysis['brute_force_ips'].items():
        print(f"  {ip}: {count} attempts")
else:
    print(f"\n✅ No brute force detected")