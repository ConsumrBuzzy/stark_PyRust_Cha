# Starkli Counterfactual Exit Commands

## Prerequisites
- starkli CLI (installation failed on Windows due to linker issues)
- Alternative: Use WSL or manual deployment

## Account Setup Commands

```bash
# Fetch account state
starkli account fetch 0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9 --network mainnet

# Export account for signing
starkli account export starknet_account --network mainnet
```

## Force Withdraw Commands

```bash
# Transfer 90% of ETH to Coinbase (leaves 10% for fees)
# Amount: 0.008157 ETH * 0.9 = 0.0073413 ETH
# In wei: 7341300000000000

starkli invoke eth transfer 0xYourCoinbaseStarknetAddr 7341300000000000 0 --account starknet_account --network mainnet
```

## Alternative: Python-based Counterfactual Exit

Since starkli failed to install on Windows, use this Python approach:

```python
# Direct contract call to transfer from counterfactual account
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.client_models import Call

# Setup
account_address = "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
private_key = "0x06d44f5b497e5222d3c6fe5158d3b73a575450575b99d2101c5c180d07bc318b"
target_address = "0xYourCoinbaseStarknetAddr"
amount = 7341300000000000  # 0.0073413 ETH in wei

# Create transfer call
eth_address = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
transfer_call = Call(
    to_addr=int(eth_address, 16),
    selector=get_selector_from_name("transfer"),
    calldata=[int(target_address, 16), amount]
)

# Sign and execute (requires deployed account)
```

## Status
- ❌ starkli installation failed on Windows (linker errors)
- ✅ Commands documented for manual execution
- ⚠️ Counterfactual exit requires deployed account or alternative method
