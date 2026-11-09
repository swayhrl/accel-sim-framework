"""CPU-only preflight and Python network guard for the frozen Q1 runner.

The AlexNet weights are a required LPIPS dependency of the original trainer.
Missing weights must stop before GPU admission; disabling LPIPS is not a fix.
"""

import hashlib
import ipaddress
import os
import socket
import urllib.parse
import urllib.request
from pathlib import Path


ALEXNET_NAME = "alexnet-owt-7be5be79.pth"
ALEXNET_SIZE = 244_408_911
ALEXNET_SHA256 = "7be5be791159472b1fbf3c69796f7cb30dca7ad8466c2df70058c37116cdee02"


class AssetPreflightError(RuntimeError):
    pass


def verify_alexnet(torch_home, *, expected_size=ALEXNET_SIZE, expected_sha256=ALEXNET_SHA256):
    """Verify the exact offline asset used by torchvision, without imports or downloads."""
    root = Path(torch_home)
    path = root / "hub" / "checkpoints" / ALEXNET_NAME
    if (not root.is_dir() or root.is_symlink() or (root / "hub").is_symlink()
            or path.parent.is_symlink() or path.is_symlink()):
        raise AssetPreflightError("AlexNet cache path is missing or contains a symlink")
    try:
        size = path.stat().st_size
    except FileNotFoundError as exc:
        raise AssetPreflightError(f"Required offline AlexNet asset is missing: {path}") from exc
    if size != expected_size:
        raise AssetPreflightError(f"AlexNet asset size mismatch: {size} != {expected_size}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest()
    if actual != expected_sha256:
        raise AssetPreflightError(f"AlexNet asset SHA-256 mismatch: {actual}")
    return {"path": str(path), "size_bytes": size, "sha256": actual}


def _local_address(address):
    if address is None:
        return True
    if isinstance(address, (str, bytes, os.PathLike)):
        return True  # AF_UNIX local IPC, including CPUAdam and local gates.
    if not isinstance(address, tuple) or not address:
        return False
    host = address[0]
    if isinstance(host, bytes):
        host = host.decode("ascii", errors="ignore")
    if host is None or host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class ExternalNetworkGuard:
    """Block Python outbound non-loopback sockets and external DNS resolution."""

    def __init__(self):
        self.original_connect = socket.socket.connect
        self.original_connect_ex = socket.socket.connect_ex
        self.original_getaddrinfo = socket.getaddrinfo
        self.original_urlopen = urllib.request.urlopen
        self.original_urlretrieve = urllib.request.urlretrieve
        self.proxy_env = {}
        self.no_proxy_env = {}
        self.installed = False

    def install(self):
        if self.installed:
            return self
        for key in tuple(os.environ):
            if key.lower() in {"http_proxy", "https_proxy", "all_proxy", "ftp_proxy"}:
                self.proxy_env[key] = os.environ.pop(key)
            elif key.lower() == "no_proxy":
                self.no_proxy_env[key] = os.environ.pop(key)
        os.environ["NO_PROXY"] = "localhost,127.0.0.1,::1"
        os.environ["no_proxy"] = "localhost,127.0.0.1,::1"

        original_connect = self.original_connect
        original_connect_ex = self.original_connect_ex
        original_getaddrinfo = self.original_getaddrinfo
        original_urlopen = self.original_urlopen
        original_urlretrieve = self.original_urlretrieve

        def check_url(url):
            value = url.full_url if isinstance(url, urllib.request.Request) else str(url)
            parsed = urllib.parse.urlsplit(value)
            if parsed.scheme in {"http", "https"} and not _local_address((parsed.hostname, parsed.port)):
                raise PermissionError(f"External URL denied: {parsed.hostname!r}")

        def connect(sock, address):
            if sock.family != socket.AF_UNIX and not _local_address(address):
                raise PermissionError(f"External network connection denied: {address!r}")
            return original_connect(sock, address)

        def connect_ex(sock, address):
            if sock.family != socket.AF_UNIX and not _local_address(address):
                raise PermissionError(f"External network connection denied: {address!r}")
            return original_connect_ex(sock, address)

        def getaddrinfo(host, port, *args, **kwargs):
            if not _local_address((host, port)):
                raise PermissionError(f"External name resolution denied: {host!r}")
            return original_getaddrinfo(host, port, *args, **kwargs)

        def urlopen(url, *args, **kwargs):
            check_url(url)
            return original_urlopen(url, *args, **kwargs)

        def urlretrieve(url, *args, **kwargs):
            check_url(url)
            return original_urlretrieve(url, *args, **kwargs)

        socket.socket.connect = connect
        socket.socket.connect_ex = connect_ex
        socket.getaddrinfo = getaddrinfo
        urllib.request.urlopen = urlopen
        urllib.request.urlretrieve = urlretrieve
        self.installed = True
        return self

    def restore(self):
        """For isolated CPU tests; production workers retain the guard until exit."""
        if self.installed:
            socket.socket.connect = self.original_connect
            socket.socket.connect_ex = self.original_connect_ex
            socket.getaddrinfo = self.original_getaddrinfo
            urllib.request.urlopen = self.original_urlopen
            urllib.request.urlretrieve = self.original_urlretrieve
            os.environ.pop("NO_PROXY", None)
            os.environ.pop("no_proxy", None)
            os.environ.update(self.proxy_env)
            os.environ.update(self.no_proxy_env)
            self.installed = False


def install_external_network_guard():
    return ExternalNetworkGuard().install()


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 offline_asset_guard.py TORCH_HOME")
    try:
        print(json.dumps(verify_alexnet(sys.argv[1]), sort_keys=True))
    except AssetPreflightError as exc:
        print(f"OFFLINE_ASSET_NO_GO: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
