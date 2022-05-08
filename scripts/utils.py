from brownie import accounts, config, network

NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development"]
FORKED_BLOCKCHAIN_ENVIRONMENTS = []
LOCAL_BLOCKCHAIN_ENVIRONMENTS = (
    NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + FORKED_BLOCKCHAIN_ENVIRONMENTS
)


def get_account(index=None):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if index:
            return accounts[index]
        return accounts[0]
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None
