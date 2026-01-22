#!/usr/bin/env python3
"""
Debug script to see what data the Avalon Nano 3S is actually returning
"""
import socket
import json

def send_command(ip, command, port=4028):
    """Send command to CGMiner API"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((ip, port))

        request = json.dumps({"command": command})
        sock.sendall(request.encode())

        response = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk

        sock.close()

        # Strip null bytes
        response_str = response.decode().rstrip('\x00')
        return json.loads(response_str)

    except Exception as e:
        print(f"Error: {e}")
        return None

MINER_IP = "10.0.0.182"

print("=== SUMMARY ===")
summary = send_command(MINER_IP, "summary")
if summary:
    print(json.dumps(summary, indent=2))

print("\n\n=== DEVS ===")
devs = send_command(MINER_IP, "devs")
if devs:
    print(json.dumps(devs, indent=2))

print("\n\n=== STATS ===")
stats = send_command(MINER_IP, "stats")
if stats:
    print(json.dumps(stats, indent=2))

print("\n\n=== POOLS ===")
pools = send_command(MINER_IP, "pools")
if pools:
    print(json.dumps(pools, indent=2))
