#!/usr/bin/env python3
"""
Test script for Avalon Nano 3S API detection
"""
import socket
import json

def test_cgminer_api(ip, port=4028):
    """Test if CGMiner API is accessible"""
    print(f"\n=== Testing CGMiner API on {ip}:{port} ===")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        print(f"Connecting to {ip}:{port}...")
        sock.connect((ip, port))
        print("✓ Connection successful!")

        # Try version command
        print("\nSending 'version' command...")
        request = json.dumps({"command": "version"})
        sock.sendall(request.encode())

        response = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk

        sock.close()

        print(f"Raw response: {response[:500]}")  # First 500 chars

        try:
            # Strip null bytes that some miners append
            response_str = response.decode().rstrip('\x00')
            data = json.loads(response_str)
            print("\n✓ Valid JSON response:")
            print(json.dumps(data, indent=2))
            return True
        except json.JSONDecodeError as e:
            print(f"✗ Response is not valid JSON: {e}")
            return False

    except socket.timeout:
        print("✗ Connection timed out")
        return False
    except ConnectionRefusedError:
        print("✗ Connection refused - port may be closed or wrong")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_http_api(ip, port=80):
    """Test if there's an HTTP API"""
    print(f"\n=== Testing HTTP API on {ip}:{port} ===")
    try:
        import requests
        print(f"Trying GET request to http://{ip}:{port}/api/stats ...")
        response = requests.get(f"http://{ip}:{port}/api/stats", timeout=5)
        print(f"✓ HTTP {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return True
    except ImportError:
        print("⚠ 'requests' module not installed, skipping HTTP test")
        print("  Install with: pip install requests")
        return False
    except Exception as e:
        print(f"✗ HTTP request failed: {e}")
        return False

if __name__ == "__main__":
    # CHANGE THIS TO YOUR MINER'S IP
    MINER_IP = "10.0.0.182"  # <-- UPDATE THIS!

    if "XXX" in MINER_IP:
        print("⚠ Please edit this file and set MINER_IP to your Avalon Nano 3S IP address")
        exit(1)

    print(f"Testing Avalon Nano 3S at {MINER_IP}")
    print("=" * 60)

    # Test standard CGMiner API port
    cgminer_works = test_cgminer_api(MINER_IP, 4028)

    # Test HTTP API
    http_works = test_http_api(MINER_IP, 80)

    # Try alternative ports
    if not cgminer_works:
        print("\n\nTrying alternative ports...")
        for port in [4029, 4030, 8080, 8000]:
            print(f"\n--- Testing port {port} ---")
            test_cgminer_api(MINER_IP, port)

    print("\n" + "=" * 60)
    print("Summary:")
    if cgminer_works:
        print("✓ CGMiner API is accessible - detection should work")
        print("  If scanner still doesn't find it, the scanner config may need adjustment")
    else:
        print("✗ CGMiner API not responding on standard port")
        print("  The Avalon Nano 3S may require custom API support")
        print("  Next steps:")
        print("  1. Check Avalon documentation for API details")
        print("  2. Add custom Avalon Nano 3S handler to the fleet manager")
