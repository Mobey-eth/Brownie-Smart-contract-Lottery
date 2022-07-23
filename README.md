1. users can enter Lottery with ETH based on USD fee
2. an admin will choose when the lottery is over
3. The lottery will select a random winner

TO GET A PSEUDO-RANDOM NUMBER(NOT RECOMMENDED)
    function endLottery() public onlyOwner {
        uint256(
            keccak256(
                abi.encodePacked(
                    nonce,
                    msg.sender,
                    block.difficulty,
                    block.timestamp
                )
            )
        ) % players.length;
    }