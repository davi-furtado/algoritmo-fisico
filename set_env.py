import socket as sc

s = sc.socket(sc.AF_INET, sc.SOCK_DGRAM)
s.connect(('10.255.255.255', 1))
ip = s.getsockname()[0]
s.close()

print(ip)

with open('mobile/.env', 'w') as f:
    f.write(f'IP={ip}')