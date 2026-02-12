from web3 import Web3
import sys

def verify_tx(tx_hash):
    w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
    try:
        print(f"Checking Base Hash: {tx_hash}")
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        if receipt.status == 1:
            print("✅ SUCCESS: Transaction confirmed on Base.")
            print(f"Block Number: {receipt.blockNumber}")
            print(f"Gas Used: {receipt.gasUsed}")
        else:
            print("❌ FAILED: Transaction failed on Base.")
    except Exception as e:
        print(f"⌛ PENDING or NOT FOUND: {e}")

if __name__ == "__main__":
    h = "0x2dec7c24a1b11c731a25fd8c7c2e681488e0c58730ba82f9d20d46032a263407"
    verify_tx(h)
