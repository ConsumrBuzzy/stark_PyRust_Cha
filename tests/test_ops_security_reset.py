import os
import sys
import types

# Stub EncryptedSigner
class DummyEncryptedSigner:
    def __init__(self):
        self._pk = None

    def encrypt_private_key(self, pk, password):
        self._pk = pk + password
        return True

    def decrypt_private_key(self, password=None):
        if self._pk is None:
            return None
        # stored as pk+password
        return self._pk.replace(password or "", "")

    def get_security_info(self):
        return {"key_file_exists": True, "salt_file_exists": True, "encryption_ready": True}

    def get_starknet_keypair(self, password=None):
        return {"address": "0xabc"} if self._pk else None


# Monkeypatch core.safety.EncryptedSigner import
sys.modules["core"] = types.ModuleType("core")
sys.modules["core.safety"] = types.ModuleType("core.safety")
sys.modules["core.safety"].EncryptedSigner = DummyEncryptedSigner

os.environ["STARKNET_PRIVATE_KEY"] = "0xpriv"

from src.ops.security_reset import reset_security, verify_security, wipe_encrypted_files


def test_reset_security_success(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    ok = reset_security("password123", data_dir=data_dir)
    assert ok is True


def test_verify_security_success():
    info = verify_security(password="password123")
    assert "security_info" in info
