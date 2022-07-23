from brownie import (
    Contract,
    network,
    accounts,
    config,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
)
from web3 import Web3

decimals = 8
STARTING_PRICE = 200000000000
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]


def get_account(index=None, id=None):
    # accounts.add(os.get_env())
    # accounts.load("id")
    if index:
        return account[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        account = accounts[0]
        return account

    # account = accounts.add(os.getenv("private_key"))
    return accounts.add(config["wallets"]["from_key"])


def deploy_mocks():
    print("deploying Mocks...")
    account = get_account()

    MockV3Aggregator.deploy(decimals, STARTING_PRICE, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})

    # return mock_price_feed.address
    print("Mocks deployed!")


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """

    This function will grab the contact adresses from the brownie config
    if defined , otherwise it will deploy a mock contract and return that
    mock contract.

        args:
            contract_name (string)

        returns:
            brownie.network.contract.ProjectContract: The most recently
            deployed version of that contract.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            # contract type is same as MockV3Aggregator
            deploy_mocks()
        contract = contract_type[-1]
        # eg. MockV3Aggregator[-1]
    else:
        # else we walk down the config to deploy to testnet
        contract_address = config["networks"][network.show_active()][contract_name]
        # We always need address and the ABI
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
        # MockV3Aggregator.abi

    return contract


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    # working with Interfaces!!
    print("Funded link contract")
    return tx
