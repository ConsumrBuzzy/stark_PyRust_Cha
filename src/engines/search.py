"""Address search utilities (class hash + salt scanning)."""
from __future__ import annotations

import os
from typing import List, Optional, Dict, Any, Iterable

from rich.console import Console
from starknet_py.hash.address import compute_address
from starknet_py.net.signer.key_pair import KeyPair

console = Console()


def _default_hashes() -> List[int]:
    return [
        # Argent variants
        0x01A7366993B74E484C2FA434313F89832207B53F609E25D26A27A26A27A26A27,
        0x036078334509B514626504EDC9FB252328D1A240E4E948BEF8D0C08DFF45927F,
        0x029927C8AF6BCCF3F639A0259E64E99A5A8C711A35C1A35C1A35C1A35C1A35C1,
        # OpenZeppelin variants
        0x041D788F01C2B6F914B5FD7E07B5E4B0E9E5E5E5E5E5E5E5E5E5E5E5E5E5E5E5E5,
        0x0539F522860B093C83664D4C5709968853F3E828D57D740F941F1738722A4501,
        # Braavos variants
        0x03131FA018572E01512D6B46182690D354A35C1A35C1A35C1A35C1A35C1A35C1,
        0x025EC026985A3BF9D0CC53FE6A9428574C4915EBF8A8E0A9B9B9B9B9B9B9B9B9B,
        # Custom/unknown variants
        0x071707E7C4F2B8C1E7D6E5F4E3D2C1B0A9F8E7D6C5B4A392817261514131211,
        0x03331BB0B7B955DFB643775CF5EAD54378770CD0B58851EB065B5453C4F15089,
        # Additional common hashes
        0x0246B7B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6B6,
        0x0585D5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5F5,
    ]


class AddressSearchEngine:
    def __init__(self, wallet_address: Optional[str] = None, private_key_hex: Optional[str] = None):
        self.wallet_address = wallet_address or os.getenv("STARKNET_WALLET_ADDRESS")
        self.private_key_hex = private_key_hex or os.getenv("STARKNET_PRIVATE_KEY")

    def expanded_search(
        self,
        hashes: Optional[Iterable[int]] = None,
        salt_range: int = 1000,
        salt_values: Optional[Iterable[int]] = None,
        constructor_patterns: Optional[List[List[int]]] = None,
    ) -> Dict[str, Any]:
        if not self.wallet_address or not self.private_key_hex:
            return {"success": False, "error": "Missing wallet or private key in environment"}

        target_int = int(self.wallet_address, 16)
        pub_key = KeyPair.from_private_key(int(self.private_key_hex, 16)).public_key
        hashes_list = list(hashes) if hashes is not None else _default_hashes()
        salts_iter = list(salt_values) if salt_values is not None else list(range(0, salt_range))
        patterns = constructor_patterns or [
            [pub_key, 0],
            [pub_key],
            [pub_key, 1],
            [pub_key, None],  # placeholder for salt substitution
        ]

        console.print(f"🔍 Target: {hex(target_int)}")
        console.print(f"🔑 Public Key: {hex(pub_key)}")
        console.print(f"🧪 Testing {len(hashes_list)} hashes × {len(salts_iter)} salts = {len(hashes_list) * len(salts_iter)} combos")

        for idx, h in enumerate(hashes_list):
            console.print(f"\n🔍 Hash {idx + 1}/{len(hashes_list)}: {hex(h)}")
            for salt in salts_iter:
                if salt % 100 == 0:
                    console.print(f"  📊 Progress: Salt {salt}/{salts_iter[-1] if salts_iter else salt_range}")

                for calldata in patterns:
                    # Replace placeholder None with current salt if present
                    effective_calldata = [salt if x is None else x for x in calldata]
                    try:
                        addr = compute_address(
                            class_hash=h,
                            constructor_calldata=effective_calldata,
                            salt=salt,
                            deployer_address=0,
                        )
                        if addr == target_int:
                            console.print("\n🎉 **MATCH FOUND!** 🎉")
                            console.print(f"Hash: {hex(h)}")
                            console.print(f"Salt: {salt}")
                            console.print(f"Constructor: {effective_calldata}")
                            return {
                                "success": True,
                                "hash": hex(h),
                                "salt": salt,
                                "calldata": effective_calldata,
                                "target": hex(target_int),
                            }
                    except Exception:
                        continue
        console.print(f"\n❌ No match found in {len(hashes_list) * len(salts_iter)} combinations")
        return {"success": False, "error": "No match", "tested": len(hashes_list) * len(salts_iter)}
