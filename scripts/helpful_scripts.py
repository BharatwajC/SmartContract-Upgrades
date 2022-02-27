from brownie import accounts, network, config
from eth_typing import HexStr
import eth_utils
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache", "mainnet-fork"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["from_key"])



def encode_function_data(initializer = None, *args):      #*args gets any number of parameter 
   
    """Encodes the function call so we can work with an initializer.
    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: `box.store`.
        Defaults to None.
        args (Any, optional):
        The arguments to pass to the initializer function
    Returns:
        [bytes]: Return the encoded bytes.
    """
   
   
    #initizer = box.score, 1,2 3,4,5,..

    if len(args) == 0 or initializer:       # len of arguments cant be 0 we will run into issue 
        return eth_utils.to_bytes(hexstr = "0x")      #we are returning empty hex string and the smart contract will understand aah arguments are blank here

    return initializer.encode_input(*args) 

    #we are encoding ( box.store,1) it to bytes so that our smart contract will know what function to call



def upgrade(
    account, 
    proxy,          #proxy contract main parent
    new_implementation_address,     # our proxy contract in the deploy.py line 79
    proxy_admin_contract=None,  #proxy  admin contract which could be none our desired proxy contract which we wanna make it proxy
    initializer=None,   #initializer which could be none
    *args       # *args - any number of elements could be stored in this args list
    ):
        transaction = None
        if proxy_admin_contract:
            if initializer:
                encoded_function_call = encode_function_data(initializer, *args)
                transaction = proxy_admin_contract.upgradeAndCall(
                    proxy.address,
                    new_implementation_address,
                    encoded_function_call,   #bytes memory data     refer ProxyAdmin.sol
                    {"from":account},
                )
            else:
                # if they dont have an initializer we dont need to encode
                transaction = proxy_admin_contract.upgrade(
                    proxy.address,
                    new_implementation_address,
                    {"from":account}
                )    #refer ProxyAdmin.sol just 2 parameter

        #now if it doesnt have proxy admin contract this means that the admin is just going to be a regular old wallet rhen what will we do then?
        #first lets check if there is an initializer

        else:
            if initializer:
                encoded_function_call = encode_function_data(initializer, *args)
                transaction = proxy.upgradeAndCall(        #In this the main proxy the parent proxy itself acting here since there is no proxy_admin_contract defined by us
                    new_implementation_address,
                    encoded_function_call,
                    {"from":account}
                )

            else:
                transaction = proxy.upgrade(
                    new_implementation_address,
                    {"from":account},
                ) 
        return transaction


        #it is a very easy function to understand right here
        #proxy_admin_address   -  initializer yes or no
        #no proxy_admin_address - initializr yes or no

















