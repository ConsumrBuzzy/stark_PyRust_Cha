from web3 import Web3

def check_tx_details():
    w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
    tx_hash = "0x2dec7c24a1b11c731a25fd8c7c2e681488e0c58730ba82f9d20d46032a263407"
    
    try:
        tx = w3.eth.get_transaction(tx_hash)
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        
        print(f"From: {tx['from']}")
        print(f"To: {tx['to']}")
        print(f"Value: {tx['value'] / 10**18:.6f} ETH")
        print(f"Block: {receipt['blockNumber']}")
        print(f"Status: {'SUCCESS' if receipt.status == 1 else 'FAILED'}")
        print(f"Gas Used: {receipt['gasUsed']}")
        
        # Check if it's a contract interaction
        if tx['to'] and tx['input'] != '0x':
            print(f"Contract: {tx['to']}")
            print(f"Input data: {tx['input'][:50]}...")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_tx_details()
