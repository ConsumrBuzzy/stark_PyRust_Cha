"""Security reset and verification helpers wrapping core.safety.EncryptedSigner."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Dict, Any

from src.ops.env import load_dotenv

try:
    from core.safety import EncryptedSigner
except Exception:  # pragma: no cover
    EncryptedSigner = None  # type: ignore


def wipe_encrypted_files(data_dir: Path | str = Path("data")) -> None:
    data_path = Path(data_dir)
    key_file = data_path / "encrypted_keys.dat"
    salt_file = data_path / "key_salt.dat"
    if key_file.exists():
        key_file.unlink()
    if salt_file.exists():
        salt_file.unlink()


def reset_security(
    password: str,
    *,
    data_dir: Path | str = Path("data"),
    signer_factory: Callable[[], Any] | None = None,
) -> bool:
    """Reset security by wiping encrypted files and encrypting the private key with a new password."""

    load_dotenv()
    signer_cls = signer_factory or (EncryptedSigner if EncryptedSigner else None)
    if signer_cls is None:
        raise RuntimeError("EncryptedSigner not available")

    raw_pk = os.getenv("STARKNET_PRIVATE_KEY")
    if not raw_pk:
        raise RuntimeError("STARKNET_PRIVATE_KEY not set in environment")

    wipe_encrypted_files(data_dir)

    os.environ["SIGNER_PASSWORD"] = password
    signer = signer_cls()
    success = signer.encrypt_private_key(raw_pk, password)
    if not success:
        return False

    # Verify encryption
    decrypted = signer.decrypt_private_key(password)
    if decrypted != raw_pk:
        return False

    return True


def verify_security(
    password: str | None = None,
    *,
    signer_factory: Callable[[], Any] | None = None,
) -> Dict[str, Any]:
    """Verify current security state; if password provided, attempt decryption."""

    load_dotenv()
    signer_cls = signer_factory or (EncryptedSigner if EncryptedSigner else None)
    if signer_cls is None:
        raise RuntimeError("EncryptedSigner not available")

    signer = signer_cls()
    security_info = signer.get_security_info()

    result = {"security_info": security_info, "password_valid": None}
    if password:
        try:
            key = signer.decrypt_private_key(password)
            result["password_valid"] = key is not None
        except Exception:
            result["password_valid"] = False
    return result


__all__ = ["reset_security", "verify_security", "wipe_encrypted_files"]
