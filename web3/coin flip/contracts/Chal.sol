pragma solidity ^0.8.13;

contract Chal {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    // Accept ether
    receive() external payable {}

    // Simple withdraw function - players need to drain the contract
    //
    // Each flip drains 1 ETH if won. Players must do 91 flips to drain from 100 ETH to below 10 ETH.
    function flip() external payable {
        require(msg.value >= 0.05 ether, "Must send ether to flip");
        require(msg.value <= 5 ether, "Max 5 ether per flip");

        // Flip a coin
        if (uint256(blockhash(block.number - 1)) % 2 == 0) {
            // Win
            payable(msg.sender).transfer((msg.value * 6) / 5); // 20% profit
        }
    }

    // Get balance
    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }
}
