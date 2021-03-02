import sys
import socket
import time
import signal
from timeit import default_timer as timer

try:
    hostrange = sys.argv[1]
    portrange = sys.argv[2]
except IndexError:
    print("Usage: main.py hostrange [portrange]")
    sys.exit(1)

stats = {
    'Errors': [],
    'Successes': [],
    'Hosts': 0
}

def parse_range (range):
    if '-' in range:
        limits = range.split('-')
        return int(limits[0]), int(limits[1])
    else:
        return int(range), int(range)

def parse_hosts (range):
    hosts = []
    segments = range.split('.')
    for segment in segments:
        hosts.append(parse_range(segment))
        
    return hosts

def ping (host, port):
    port = int(port)
    success = False

    # New Socket
    s = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)

    # 1sec Timeout
    s.settimeout(1)

    # Start a timer
    s_start = timer()

    # Try to Connect
    try:
        s.connect((host, int(port)))
        s.shutdown(socket.SHUT_RD)
        success = True

    # Connection Timed Out
    except socket.timeout:
        stats['Errors'].append(f"Failed to connect to {host}[{port}]: timed out")
    except OSError as e:
        stats['Errors'].append(f"Failed to connect to {host}[{port}]: " + str(e))

    # Stop Timer
    s_stop = timer()
    s_runtime = "%.2f" % (1000 * (s_stop - s_start))

    if success:
        stats['Successes'].append(f"Connected to {host}[{port}]: tcp_seq=1 time={s_runtime} ms")

def exit (signal, frame):
    get_results()
    sys.exit(0)


def get_results ():
    for error in stats['Errors']:
        print(error)
    for succ in stats['Successes']:
        print(succ)
    print(f"Hosts scanned: {stats['Hosts']}")

def generate_range (_range):
    lo, hi = _range
    return range(lo, hi+1)

signal.signal(signal.SIGINT, exit)

s1, s2, s3, s4 = parse_hosts(hostrange)
p = parse_range(portrange)

for i in generate_range(s1):
    for j in generate_range(s2):
        for k in generate_range(s3):
            for l in generate_range(s4):
                for port in generate_range(p):
                    ping(f"{i}.{j}.{k}.{l}", port)
                stats['Hosts'] += 1

get_results()
