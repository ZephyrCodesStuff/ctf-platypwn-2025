# Compile the "contracts/Setup.sol" contract and get the ABI and bytecode
from solcx import install_solc, compile_standard
import json

COMPILE_OPTIONS = {
    "language": "Solidity",
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "evm.bytecode"]
            }
        }
    }
}

CONTRACTS = ["Setup.sol", "Chal.sol", "Attacker.sol"]
SOLC_VERSION = "0.8.13"

install_solc(SOLC_VERSION)

for contract in CONTRACTS:
    COMPILE_OPTIONS["sources"] = {contract: {"content": ""}}

    with open(f"contracts/{contract}", "r") as file:
        setup_source = file.read()
    
    COMPILE_OPTIONS["sources"][contract]["content"] = setup_source
    
    compiled_sol = compile_standard(COMPILE_OPTIONS, solc_version=SOLC_VERSION)
    
    with open(f"compiled_{contract}.json", "w") as file:
        json.dump(compiled_sol, file, indent=4)