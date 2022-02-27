from scripts.helpful_scripts import get_account,encode_function_data,upgrade
from brownie import network,config,Box,ProxyAdmin,TransparentUpgradeableProxy,Contract,BoxV2

def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy({"from":account}, publish_source =True)

    #print(box.retrieve())  - works fine
    # Now lets try to run Box.increment()   here increment is in contract BoxV2.sol
    #print(box.increment()) - throws error as contract box object has no attribute 'increment'

    #Hooking up a proxy to our implementation contract
      
    #Now lets give it a proxy admin             - link in the course
    #Proxy admins are optional and it is also recommended that iyf you do have a proxy admin we are going to use some defi protocol
    #sometimes its great to your proxy admin be something like multi-sig gnosis safe which is going to be fantastoic

    #Gnosis Safe is a smart contract wallet running on Ethereum that requires a minimum number of people to approve a transaction before it can occur (M-of-N).

    # check out github once

    # We could set ourselves as proxy admin but lets just make this contract be the proxy admin

    proxy_admin = ProxyAdmin.deploy({"from":account}, publish_source =True)

    #Now in proxyadmin we get to see that
    #getProxyImplementation() returns the address of implementation 
    #getproxyadmin() returns the proxy admin which is us 
    #changeProxyAdmin() changes proxy admin
    #upgrade() - it is going to call upgrade function on the proxy
    #upgradeAndCall() - changes the implementation to the new implemetation and then calls the initializer functionn


    #(NOTE: Proxies dont have  constructors)

    # Now since we want these to be proxies we dont have a contructor this is intentional
    #instead we could have some type of initializer function 
    # for example we have this store() be our constructor
    #instead of having constructor we have this initoalizer function which is called the instant we deploy the contract
    
    #But for the demo here we are not going to have any initializer 
    
    #Now,
    # box - implementation contract
    # proxy_admin - proxy
    # Now lets now hook them up to the actual proxy, the first thing we need to do actually is we have to encode the initializer function if we wanted to store to be our iitializer
    # function like

    initializer = box.store, 1  # store(uint256 newValue)  
                                #this is our initializer box.score combined with 1

    #now what we have to do is we have to encode this for our proxy
    
    #In transparentUpgradeableProxy constructor 

    # constructor(
    #     address _logic, -> our implementation - in this case our box.sol address
    #     address admin_,   -> Proxy address contract in our case its us
    #     bytes memory _data    -> the data is going to be our initializer function  
      
    # inside ERC1967/ERC1967Proxy  -> upgradeToAndCall() -> Address.functionDelegateCall(newImplementation, data); this is how is actually calls that initializer function 


    #initializer = box.store, 1   we have to encode this into bytes
    #box.store - function call
    # 1 is the first parameter 

    box_encoded_initializer_function = encode_function_data()

    #Now this (box_encoded_initializer_function) is what we use to call our transparent upgradable proxy

    # box_encoded_initializer_function = encode_function_data(initializer)  hey use an initiizer
    # box_encoded_initializer_function = encode_function_data() if its blank hey dont use an initializer
    # in our learning we are not going to use the initializer see the code above but lets try with it later 

    #Now lets deploy this transparent upgradeable proxy

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,            #implementation address
        proxy_admin.address,    # which could be us but lets give proxy_admin address
        box_encoded_initializer_function,      # we need that function selector we need that encoded function call which for us in this case is blank (0x)                       
        {"from":account, "gas_limit": 1000000 },
         publish_source =True                                           #He said its sometime good to add gas limit beacuse sometimes proxies have hardtime figuring out th egas limit
                                                        #so we manually added
    )
    
    print(f"Proxy deployed to {proxy}, you can now upgrade to v2! ")

    #Assigning ABI to a proxy


    # Now what we can do is on the proxy's address we can call the function

    #typically we call box.store(1)
    # however we want to actually call these on the proxies right because this box contracts address is always going to be the same address and cant change but the proxy code
    #can change we want to always call these functions to the proxy and not to the box here (box.store(1)) 
    # so the way we are going to do that is

    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    # what we are doing here is assigning this proxy address the abi of the box contract 
    #and this going to work because the proxy is going to work beacuse the proxy is going to delegate all of its calls
    #to the box contract 

    #Typically if you put an abi on top of an address that doesnt have those functions that the abi defines it would just give error 
    # but th eproxy is going to delegate all the calls to the box 

    #so lets try 

    proxy_box.store(1, {"from":account})
    
    print(proxy_box.retrieve())     # Instead of using box we are using using proxy by delegate calling box
    
    
    #Even though we are using proxy address here we are going to delegate the call to box

    #Now we learned how t deploy it now lets upgrade it


    #now we can always point to this proxy box address and its going to be the most recent upgrade it's always going to have the code
    #that we want it to have 
    #So now lets upgrade from Box that doesnt have that increment to BoxV2 that does indeed have the increment  

    #so lets try this out   
    #first thing we need to do is first deploy BoxV2

    box_v2 = BoxV2.deploy({"from":account}, publish_source =True)     #upgrade

    #proxy_box.increment({"from":account}) throws us error and its quite obvious as box doent have increment()

    #upgrade

    #upgrade()       
    #Basically what we have to do is call upgradeTo() function but depending on if we've added a proxy admin contract if 
    #we are using initializer function there might be a couple of different ways to go about this but lets just wrap everything 
    # up into its own upgrade function 

    box_v2 = BoxV2.deploy({"from":account})

    upgrade_transaction = upgrade(
        account,
        proxy,
        box_v2.address,
        proxy_admin_contract=proxy_admin,
        initializer=None        #we are not passing any initializer right here
    )

    upgrade_transaction.wait(1)

    print("Proxy has been upgraded!")

    proxy_box = Contract.from_abi("BoxV2",proxy.address,BoxV2.abi)

    #Now we'll be able to call increment() as we changed the implementation address to BoxV2 from Box

    proxy_box.increment({"from":account})

    print(proxy_box.retrieve())     #The o.p we expect is 2 

    # so why does it return 2 well in our original proxy box we stored 1 and then we upgraded to new contract 
    #right above (upgrade_transaction) however the storage of the contract stayed in the proxy so 1 stayed in the proxy so even though we uograded the contract
    # there's still 1 stored at the location in the storage so when we call the increment now and then we call retreive it's gonna go from 1 to 2

    # so lets run this
    #it worked fine

    #lets write test
    


