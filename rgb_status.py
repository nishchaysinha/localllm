#!/usr/bin/env python3
"""
LLM RGB Status Light

Polls the vLLM server and changes OpenRGB colors based on activity:
  - Idle:       Soft cyan
  - Generating: Purple
  - Error/Down: Red
  - Starting:   Orange

Connects to OpenRGB via SDK server (port 6742).
Make sure OpenRGB is running with: Settings > SDK Server > Enable
"""

import os
import sys
import time
import socket
import struct
import urllib.request

VLLM_URL = os.environ.get("VLLM_URL", "http://localhost:8000")
VLLM_API_KEY = os.environ.get("VLLM_API_KEY", "")
POLL_INTERVAL = float(os.environ.get("RGB_POLL_INTERVAL", "0.5"))
OPENRGB_HOST = os.environ.get("OPENRGB_HOST", "127.0.0.1")
OPENRGB_PORT = int(os.environ.get("OPENRGB_PORT", "6742"))

# Colors (R, G, B)
COLORS = {
    "idle": tuple(int(os.environ.get("RGB_COLOR_IDLE", "00CCAA")[i:i+2], 16) for i in (0, 2, 4)),
    "active": tuple(int(os.environ.get("RGB_COLOR_ACTIVE", "AA00FF")[i:i+2], 16) for i in (0, 2, 4)),
    "error": tuple(int(os.environ.get("RGB_COLOR_ERROR", "FF0000")[i:i+2], 16) for i in (0, 2, 4)),
    "starting": tuple(int(os.environ.get("RGB_COLOR_STARTING", "FFAA00")[i:i+2], 16) for i in (0, 2, 4)),
}

current_state = None


class OpenRGBClient:
    """Minimal OpenRGB SDK client — no dependencies needed."""

    HEADER_FMT = "4sIII"  # magic, device_id, packet_type, length
    MAGIC = b"ORGB"

    # Packet types
    NET_PACKET_ID_SET_CLIENT_NAME = 50
    NET_PACKET_ID_REQUEST_CONTROLLER_COUNT = 0
    NET_PACKET_ID_REQUEST_CONTROLLER_DATA = 1
    NET_PACKET_ID_UPDATE_LEDS = 1050

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(3)
            self.sock.connect((self.host, self.port))
            # Send client name
            name = b"LLM-RGB-Status\x00"
            header = struct.pack(self.HEADER_FMT, self.MAGIC, 0,
                                 self.NET_PACKET_ID_SET_CLIENT_NAME, len(name))
            self.sock.sendall(header + name)
            return True
        except Exception as e:
            print(f"[RGB] OpenRGB connection failed: {e}", flush=True)
            self.sock = None
            return False

    def get_controller_count(self):
        header = struct.pack(self.HEADER_FMT, self.MAGIC, 0,
                             self.NET_PACKET_ID_REQUEST_CONTROLLER_COUNT, 0)
        self.sock.sendall(header)
        resp_header = self.sock.recv(16)
        _, _, _, length = struct.unpack(self.HEADER_FMT, resp_header)
        data = self.sock.recv(length)
        return struct.unpack("I", data)[0]

    def set_all_colors(self, r, g, b):
        """Set all LEDs on all controllers to the given color."""
        if not self.sock:
            return False
        try:
            count = self.get_controller_count()
            for dev_id in range(count):
                # Request controller data to get LED count
                header = struct.pack(self.HEADER_FMT, self.MAGIC, dev_id,
                                     self.NET_PACKET_ID_REQUEST_CONTROLLER_DATA, 0)
                self.sock.sendall(header)
                resp_header = self.sock.recv(16)
                _, _, _, length = struct.unpack(self.HEADER_FMT, resp_header)
                data = b""
                while len(data) < length:
                    chunk = self.sock.recv(min(4096, length - len(data)))
                    if not chunk:
                        break
                    data += chunk

                # Parse num_leds from controller data (at offset varies, use num_colors)
                # The LED count is embedded in the data structure
                # Simpler: just send 512 LEDs worth (excess is ignored)
                num_leds = 512
                # Build LED update packet
                led_data = struct.pack("H", num_leds)
                for _ in range(num_leds):
                    led_data += struct.pack("BBBB", r, g, b, 0)

                header = struct.pack(self.HEADER_FMT, self.MAGIC, dev_id,
                                     self.NET_PACKET_ID_UPDATE_LEDS,
                                     len(led_data))
                self.sock.sendall(header + led_data)
            return True
        except Exception as e:
            print(f"[RGB] Set color error: {e}", flush=True)
            self.sock = None
            return False

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None


def get_active_requests():
    """Check llama.cpp metrics for active request count."""
    try:
        req = urllib.request.Request(f"{VLLM_URL}/metrics")
        if VLLM_API_KEY:
            req.add_header("Authorization", f"Bearer {VLLM_API_KEY}")
        with urllib.request.urlopen(req, timeout=2) as resp:
            text = resp.read().decode()
            for line in text.split("\n"):
                if line.startswith("llamacpp:requests_processing"):
                    return int(float(line.split()[-1]))
            return 0
    except Exception:
        return -1


def main():
    print("[RGB] LLM Status Light starting...", flush=True)
    print(f"[RGB] vLLM: {VLLM_URL}", flush=True)
    print(f"[RGB] OpenRGB: {OPENRGB_HOST}:{OPENRGB_PORT}", flush=True)

    global current_state
    client = OpenRGBClient(OPENRGB_HOST, OPENRGB_PORT)

    while True:
        try:
            # Ensure connection
            if not client.sock:
                if not client.connect():
                    print("[RGB] Waiting for OpenRGB SDK server...", flush=True)
                    time.sleep(5)
                    continue
                print("[RGB] Connected to OpenRGB.", flush=True)
                r, g, b = COLORS["starting"]
                client.set_all_colors(r, g, b)
                current_state = "starting"

            active = get_active_requests()

            if active < 0:
                new_state = "error"
            elif active > 0:
                new_state = "active"
            else:
                new_state = "idle"

            if new_state != current_state:
                r, g, b = COLORS[new_state]
                if client.set_all_colors(r, g, b):
                    current_state = new_state
                    print(f"[RGB] State: {new_state}", flush=True)

        except KeyboardInterrupt:
            print("\n[RGB] Shutting down...", flush=True)
            r, g, b = COLORS["idle"]
            client.set_all_colors(r, g, b)
            client.close()
            break
        except Exception as e:
            print(f"[RGB] Error: {e}", flush=True)
            client.close()

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
