from asyncio import exceptions
from scripts.deploy_lottery import deploy_lottery
from brownie import accounts, Lottery, network, config, exceptions
from web3 import Web3
import pytest
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    fund_with_link,
    get_account,
    get_contract,
)


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    # 2000 eth/usd fee but entry fee = $50
    entrance_fee = lottery.getEntranceFee()
    expected_entranceFee = Web3.toWei(0.025, "ether")
    # Assert
    assert entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    # Act/ assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    # Act/ assert
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 1000000})
    assert lottery.players(0) == account


def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 1000000})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 1000000})
    lottery.enter({"from": accounts[1], "value": lottery.getEntranceFee() + 1000000})
    lottery.enter({"from": accounts[2], "value": lottery.getEntranceFee() + 1000000})
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RANDNUM = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RANDNUM, lottery.address, {"from": account}
    )
    # ie 777 % 3 = 0
    startingbalance_of_account = account.balance()
    balance_of_lottery = lottery.balance()

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == startingbalance_of_account + balance_of_lottery


# Omoo
