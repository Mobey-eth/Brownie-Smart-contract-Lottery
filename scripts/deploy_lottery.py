from brownie import Lottery, accounts, config, network
from scripts.helpful_scripts import get_account, get_contract, fund_with_link
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    time.sleep(1)
    print("Deployed lottery!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    lottery.startLottery({"from": account})
    print("The lottery is started!")
    time.sleep(1)


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 1000000
    lottery.enter({"from": account, "value": value})
    print("You have entered the lottery!")
    time.sleep(1)


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # fund with link
    # end the lottery
    fund_with_link(lottery.address)
    ending_txn = lottery.endLottery({"from": account})
    time.sleep(300)
    print(f"{lottery.recentWinner()} is the new winner!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
