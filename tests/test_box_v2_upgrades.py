from xmlrpc.client import Transport
from scripts.helpful_scripts import upgrade,encode_function_data, get_account
from brownie import Box,ProxyAdmin,TransparentUpgradeableProxy,Contract,BoxV2
from brownie import exceptions
import pytest

def test_proxy_upgrades():
    account = get_account()
    box = Box.deploy({"from":account})
    proxy_admin = ProxyAdmin.deploy({"from":account}) 
    box_encoded_initializer_function = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from":account,"gas_limit":1000000}
    ) 

    #We already tested previously that proxy works fine

    # Now we are goong to upgrade the proxy and check everything works fine

    box_v2 = BoxV2.deploy({"from":account})
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)

    #what we aretrying to do is slapping this abi onto this proxy.address we're are trying to call a function
    #only boxv2 here however we know that like we tested before it actually should revert  
    
    #so we are going to check reverts by importing  
    
    with pytest.raises(exceptions.VirtualMachineError):      #we can check find out the exception by just running it we'll see the error
        proxy_box.increment({"from":account})
    #calling proxy_box.increment() should throw this exceptions.virtualMachineError so this test will pass if this throws an error 
    #and thats how we test that so we want this to throw an error the first timw we call it then we're are going to upgrade and we'll call it again and it'll
    #actually work 

    #Now we are going tp call upgrade on account 

    upgrade(account, proxy, box_v2, proxy_admin_contract=proxy_admin)
    assert proxy_box.retrieve() == 0
    proxy_box.increment({"from":account})
    assert proxy_box.retrieve() == 1

    #so we are deploying our box
    # we are deploying our proxy and everything around ot 
    #then we are deployong our v2 implementation
    #we are trying to call the increment which won't  work
    #we then upgrade our proxy to this new address 
    #then we call our increment  

    #lets test brownie test -k test_box_v2_upgrades

    
