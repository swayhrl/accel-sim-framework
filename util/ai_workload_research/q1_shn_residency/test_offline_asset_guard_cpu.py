"""Pure CPU tests: no torch, CUDA, runner or external network access."""

import hashlib
import http.server
import os
import socket
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path

from offline_asset_guard import (
    ALEXNET_NAME,
    AssetPreflightError,
    install_external_network_guard,
    verify_alexnet,
)


class AssetTests(unittest.TestCase):
    def test_missing_and_wrong_asset_fail_before_use(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp)
            with self.assertRaises(AssetPreflightError):
                verify_alexnet(cache, expected_size=4, expected_sha256=hashlib.sha256(b"good").hexdigest())
            target = cache / "hub" / "checkpoints" / ALEXNET_NAME
            target.parent.mkdir(parents=True)
            target.write_bytes(b"bad!")
            with self.assertRaisesRegex(AssetPreflightError, "SHA-256 mismatch"):
                verify_alexnet(cache, expected_size=4, expected_sha256=hashlib.sha256(b"good").hexdigest())
            with self.assertRaisesRegex(AssetPreflightError, "size mismatch"):
                verify_alexnet(cache, expected_size=5, expected_sha256=hashlib.sha256(b"bad!").hexdigest())
            target.write_bytes(b"good")
            self.assertEqual(
                verify_alexnet(cache, expected_size=4, expected_sha256=hashlib.sha256(b"good").hexdigest())["size_bytes"],
                4,
            )

    def test_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp)
            target = cache / "hub" / "checkpoints" / ALEXNET_NAME
            target.parent.mkdir(parents=True)
            source = cache / "source"
            source.write_bytes(b"good")
            target.symlink_to(source)
            with self.assertRaises(AssetPreflightError):
                verify_alexnet(cache, expected_size=4, expected_sha256=hashlib.sha256(b"good").hexdigest())


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"local gate ok")

    def log_message(self, *_):
        pass


class NetworkTests(unittest.TestCase):
    def test_external_denied_local_gate_and_unix_ipc_allowed(self):
        server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
        thread = threading.Thread(target=server.handle_request, daemon=True)
        thread.start()
        guard = install_external_network_guard()
        try:
            with self.assertRaises(PermissionError):
                socket.getaddrinfo("download.pytorch.org", 443)
            with self.assertRaises(PermissionError):
                urllib.request.urlopen("https://download.pytorch.org/models/alexnet-owt-7be5be79.pth", timeout=2)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as external:
                with self.assertRaises(PermissionError):
                    external.connect(("8.8.8.8", 443))
            with urllib.request.urlopen(f"http://127.0.0.1:{server.server_port}/status", timeout=2) as response:
                self.assertEqual(response.read(), b"local gate ok")
            left, right = socket.socketpair()
            try:
                left.send(b"ipc")
                self.assertEqual(right.recv(3), b"ipc")
            finally:
                left.close()
                right.close()
        finally:
            guard.restore()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
