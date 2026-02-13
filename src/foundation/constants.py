"""
PyPro Systems - Foundation Constants
Centralized configuration and constants
"""

# Network Constants
BASE_RPC_URL = "https://mainnet.base.org"
STARKNET_RPC_URL = "https://starknet-mainnet.g.alchemy.com/starknet/version/rpc/v0_10/9HtNv_yFeMgWsbW_gI2IN"

# Contract Addresses
STARGATE_BRIDGE_ADDRESS = "0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419"
STARKNET_ETH_CONTRACT = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"

# StarkNet v0.14 Constants
STARKNET_VERSION = "0.14.0"
ACCOUNT_CLASS_HASH = "0x03131fa018d520a034689b29a785f48d7210eae8a5e759dc432a44372e201d4f"  # Argent v0.4.0

# Financial Constants
ACTIVATION_THRESHOLD = 0.018  # ETH
GAS_RESERVE = 0.001  # ETH
MIN_BRIDGE_AMOUNT = 0.001  # ETH
MAX_FEE = 0.02  # ETH

# Timing Constants
BALANCE_CHECK_INTERVAL = 30  # seconds
BRIDGE_TIMEOUT = 300  # seconds
ACTIVATION_TIMEOUT = 600  # seconds

# Security Constants
MASTER_PASSWORD_ENV = "SIGNER_PASSWORD"
PHANTOM_PRIVATE_KEY_ENV = "PHANTOM_BASE_PRIVATE_KEY"
SOLANA_PRIVATE_KEY_ENV = "SOLANA_PRIVATE_KEY"

# File Paths
STATE_FILE_PATH = "data/recovery_state.json"
LOG_FILE_PATH = "logs/recovery.log"
