from brownie import *

import time
import json
import sys
import csv
import math

def main():
    loadConfig()

    balanceBefore = acct.balance()
    choice()
    balanceAfter = acct.balance()

    print("=============================================================")
    print("RSK Before Balance:  ", balanceBefore)
    print("RSK After Balance:   ", balanceAfter)
    print("Gas Used:            ", balanceBefore - balanceAfter)
    print("=============================================================")

# =========================================================================================================================================
def loadConfig():
    global values, acct, thisNetwork
    thisNetwork = network.show_active()

    if thisNetwork == "development":
        acct = accounts[0]
        configFile = open('./scripts/values/development.json')
    elif thisNetwork == "testnet":
        acct = accounts.load("rskdeployer")
        configFile = open('./scripts/values/testnet.json')
    elif thisNetwork == "rsk-testnet":
        acct = accounts.load("rskdeployer")
        configFile = open('./scripts/values/testnet.json')
    elif thisNetwork == "rsk-mainnet":
        acct = accounts.load("rskdeployer")
        configFile = open('./scripts/values/mainnet.json')
    else:
        raise Exception("Network not supported.")

    # Load deployment parameters and contracts addresses
    values = json.load(configFile)

# =========================================================================================================================================
def choice():
    repeat = True
    while(repeat):
        print("\nOptions:")
        print("1 for Deploying Origins.")
        print("2 for Updating/Adding Deposit Address.")
        print("3 for Setting Locked Fund.")
        print("4 for Creating a new Tier.")
        print("5 for Setting Tier Verification.")
        print("6 for Setting Tier Deposit Parameters.")
        print("7 for Setting Tier Token Limit Parameters.")
        print("8 for Setting Tier Token Amount Parameters.")
        print("9 for Setting Tier Vest or Lock Parameters.")
        print("10 for Setting Tier Time Parameters.")
        print("11 for Buying Tokens.")
        print("12 for Adding Myself as a Verifier.")
        print("13 for Verifying Wallet List with Tier ID")
        print("14 for Removing Myself as an Owner.")
        print("15 for Removing Myself as a Verifier.")
        print("16 for getting the Tier Count.")
        print("17 for getting the Tier Details.")
        print("18 for getting the Owner Details.")
        print("19 for getting the Verifier Details.")
        print("20 to exit.")
        selection = int(input("Enter the choice: "))
        if(selection == 1):
            deployOrigins()
        elif(selection == 2):
            updateDepositAddress()
        elif(selection == 3):
            updateLockedFund()
        elif(selection == 4):
            createNewTier()
        elif(selection == 5):
            setTierVerification()
        elif(selection == 6):
            setTierDeposit()
        elif(selection == 7):
            setTierTokenLimit()
        elif(selection == 8):
            setTierTokenAmount()
        elif(selection == 9):
            setTierVestOrLock()
        elif(selection == 10):
            setTierTime()
        elif(selection == 11):
            buyTokens()
        elif(selection == 12):
            addMyselfAsVerifier()
        elif(selection == 13):
            verifyWallet()
        elif(selection == 14):
            removeMyselfAsOwner()
        elif(selection == 15):
            removeMyselfAsVerifier()
        elif(selection == 16):
            getTierCount()
        elif(selection == 17):
            getTierDetails()
        elif(selection == 18):
            getOwnerList()
        elif(selection == 19):
            getVerifierList()
        elif(selection == 20):
            repeat = False
        else:
            print("\nSmarter people have written this, enter valid selection ;)\n")

# =========================================================================================================================================
def deployOrigins():
    adminList = [values['multisig'], values['initialAdmin']]
    token = values['token']
    depositAddress = values['depositAddress']

    print("\n=============================================================")
    print("Deployment Parameters for Origins")
    print("=============================================================")
    print("Admin List:          ", adminList)
    print("Token Address:       ", token)
    print("Deposit Address:     ", depositAddress)
    print("=============================================================")

    origins = acct.deploy(OriginsBase, adminList, token, depositAddress)

    print("\nOrigins Deployed.")

    values['origins'] = str(origins)
    writeToJSON()

    updateLockedFund()

    lockedFund = Contract.from_abi("LockedFund", address=values['lockedFund'], abi=LockedFund.abi, owner=acct)

    print("\nAdding Origins as an admin to LockedFund...\n")
    lockedFund.addAdmin(values['origins'])
    print("Added Origins as", values['origins'], " as an admin of Locked Fund.")

    addMyselfAsVerifier()

    getOwnerList()

    getVerifierList()

# =========================================================================================================================================
def updateDepositAddress():
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)
    print("\nUpdating Deposit Address of Origins...\n")
    origins.setDepositAddress(values['depositAddress'])
    print("Updated Deposit Address as", values['depositAddress'], " of Origins...\n")

# =========================================================================================================================================
def updateLockedFund():
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)
    print("\nUpdating Locked Fund Contract Address of Origins...\n")
    origins.setLockedFund(values['lockedFund'])
    print("Updated Locked Fund Contract Address as", values['lockedFund'], " of Origins...\n")

# =========================================================================================================================================
def readTier(reason):
    print("\nIf you want to",reason,"the first tier, i.e. Index = 1 in JSON `tiers`, enter 1.")
    tierID = int(input("Enter the Tier ID (Based on JSON File): "))
    return tierID

# =========================================================================================================================================
def getDepositType(depositType):
    if depositType == 0:
        return "RBTC"
    elif depositType == 1:
        return "Token"
    else:
        return "Invalid Entry!"

# =========================================================================================================================================
def getVerificationType(verificationType):
    if verificationType == 0:
        return "None"
    elif verificationType == 1:
        return "Everyone"
    elif verificationType == 2:
        return "ByAddress"
    else:
        return "Invalid Entry!"

# =========================================================================================================================================
def getSaleEndDurationOrTS(saleEndDurationOrTimestamp):
    if saleEndDurationOrTimestamp == 0:
        return "None"
    elif saleEndDurationOrTimestamp == 1:
        return "UntilSupply"
    elif saleEndDurationOrTimestamp == 2:
        return "Duration"
    elif saleEndDurationOrTimestamp == 3:
        return "Timestamp"
    else:
        return "Invalid Entry!"

# =========================================================================================================================================
def getTransferType(transferType):
    if transferType == 0:
        return "None"
    elif transferType == 1:
        return "Unlocked"
    elif transferType == 2:
        return "WaitedUnlock"
    elif transferType == 3:
        return "Vested"
    elif transferType == 4:
        return "Locked"
    else:
        return "Invalid Entry!"

# =========================================================================================================================================
def makeAllowance(tokenObj, spender, amount):
    print("\nApproving Token Transfer from", acct, " to", spender)
    tokenObj.approve(spender, amount)
    print("Token Transfer Approved...")

# =========================================================================================================================================
def checkAllowance(tokenObj, spender, amount):
    if(tokenObj.allowance(acct, spender) < amount):
        if thisNetwork == "rsk-mainnet":
            print("\nNot enough token approved. Please approve the spender.")
            print("1 for approve.")
            print("Anything else for exit.")
            selection = int(input("Enter Choice: "))
            if(selection == 1):
                makeAllowance(tokenObj, spender, amount)
            else:
                sys.exit()
        else:
            makeAllowance(tokenObj, spender, amount)

# =========================================================================================================================================
def createNewTier():
    tierID = readTier("add")

    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)

    # IMPORTANT TODO: It is removed for the current sale, but has to be reimplemented in the future.
    # minAmount = values['tiers'][tierID]['minimumAmount']

    maxAmount = values['tiers'][tierID]['maximumAmount']
    tokensForSale = int(values['tiers'][tierID]['tokensForSale'])
    decimal = int(values['decimal'])
    remainingTokens = tokensForSale * (10 ** decimal)
    saleStartTimestamp = values['tiers'][tierID]['saleStartTimestamp']
    saleEnd = values['tiers'][tierID]['saleEnd']

    # IMPORTANT TODO: This needs to be changed in the future when adding Origins the capability
    # to call the Locked Fund Contract to set the waitedTS.
    # unlockedTS = values['waitedTimestamp']

    unlockedBP = values['tiers'][tierID]['unlockedBP']
    vestOrLockCliff = values['tiers'][tierID]['vestOrLockCliff']
    vestOrLockDuration = values['tiers'][tierID]['vestOrLockDuration']
    depositRate = values['tiers'][tierID]['depositRate']

    # IMPORTANT TODO: It is removed for the current sale, but has to be reimplemented in the future.
    # depositToken = values['tiers'][tierID]['depositToken']

    depositType = values['tiers'][tierID]['depositType']
    depositTypeReadable = getDepositType(int(depositType))
    verificationType = values['tiers'][tierID]['verificationType']
    verificationTypeReadable = getVerificationType(int(verificationType))
    saleEndDurationOrTimestamp = values['tiers'][tierID]['saleEndDurationOrTimestamp']
    saleEndDurationOrTimestampReadable = getSaleEndDurationOrTS(int(saleEndDurationOrTimestamp))
    transferType = values['tiers'][tierID]['transferType']
    transferTypeReadable = getTransferType(int(transferType))

    print("\n=============================================================")
    print("Tier Parameters:")
    print("=============================================================")
    # print("Minimum allowed asset:               ", minAmount)
    print("Maximum allowed asset:               ", maxAmount)
    print("Tokens For Sale (with Decimal):      ", tokensForSale)
    print("Tokens For Sale (without Decimal):   ", remainingTokens)
    print("Sale Start Timestamp:                ", saleStartTimestamp)
    print("Sale End Duration/Timestamp:         ", saleEnd)
    # print("Unlocked Token Timestamp:            ", unlockedTS)
    print("Unlocked Token Basis Point:          ", unlockedBP)
    print("Vest Or Lock Cliff:                  ", vestOrLockCliff)
    print("Vest Or Lock Duration:               ", vestOrLockDuration)
    print("Deposit Rate:                        ", depositRate)
    # print("Deposit Token:                       ", depositToken)
    print("Deposit Type:                        ", depositTypeReadable)
    print("Verification Type:                   ", verificationTypeReadable)
    print("Sale End Duration or Timestamp:      ", saleEndDurationOrTimestampReadable)
    print("Transfer Type:                       ", transferTypeReadable)
    print("=============================================================")

    if(depositTypeReadable == "Invalid Entry!" or verificationTypeReadable == "Invalid Entry!" or saleEndDurationOrTimestampReadable == "Invalid Entry!" or transferTypeReadable == "Invalid Entry!"):
        print("\nPlease check the types and tier parameters.")
        sys.exit()
    
    token = Contract.from_abi("Token", address=values['token'], abi=Token.abi, owner=acct)
    checkAllowance(token, origins.address, remainingTokens)

    balance = token.balanceOf(acct)
    print("\nCurrent User Token Balance:",balance)

    print("\nCreating new tier...")
    # Based on the new parameters added on the TODO above, need to add the parameters here as well.
    origins.createTier(maxAmount, remainingTokens, saleStartTimestamp, saleEnd, unlockedBP, vestOrLockCliff, vestOrLockDuration, depositRate, depositType, verificationType, saleEndDurationOrTimestamp, transferType)

    balance = token.balanceOf(acct)
    print("Updated User Token Balance:",balance)

# =========================================================================================================================================
def setTierVerification():
    tierID = readTier("edit")
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)
    origins.setTierVerification(tierID, values['tiers'][tierID]['verificationType'])
    print("Tier Verification Updated.")

# =========================================================================================================================================
def setTierDeposit():
    tierID = readTier("edit")
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)
    origins.setTierDeposit(tierID, values['tiers'][tierID]['depositRate'], values['tiers'][tierID]['depositToken'], values['tiers'][tierID]['depositType'])
    print("Tier Deposit Updated.")

# =========================================================================================================================================
def setTierTokenLimit():
    tierID = readTier("edit")
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)
    origins.setTierTokenLimit(tierID, values['tiers'][tierID]['minimumAmount'], values['tiers'][tierID]['maximumAmount'])
    print("Tier Token Limit Updated.")

# =========================================================================================================================================
def setTierTokenAmount():
    tierID = readTier("edit")
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)
    tokensForSale = int(values['tiers'][tierID]['tokensForSale'])
    decimal = int(values['decimal'])
    remainingTokens = tokensForSale * (10 ** decimal)
    origins.setTierTokenAmount(tierID, remainingTokens)
    print("Tier Token Amount Updated.")

# =========================================================================================================================================
def setTierVestOrLock():
    tierID = readTier("edit")
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)
    origins.setTierVestOrLock(tierID, values['tiers'][tierID]['vestOrLockCliff'], values['tiers'][tierID]['vestOrLockDuration'], values['waitedTimestamp'], values['tiers'][tierID]['unlockedBP'], values['tiers'][tierID]['transferType'])
    print("Tier Vest or Lock Updated.")

# =========================================================================================================================================
def setTierTime():
    tierID = readTier("edit")
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)
    origins.setTierTime(tierID, values['tiers'][tierID]['saleStartTimestamp'], values['tiers'][tierID]['saleEnd'], values['tiers'][tierID]['saleEndDurationOrTimestamp'])
    print("Tier Time Updated.")

# =========================================================================================================================================
def buyTokens():
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)
    tierID = readTier("buy tokens in")
    amount = 0
    rbtcAmount = 0
    print("\nIf you want to send just `X` RBTC/Token, put 1 itself, (X * (10 ** Decimals)) is done behind the screen.")
    amount = int(input("Enter the amount of tokens/RBTC you want to send: "))
    if(values['tiers'][tierID]['depositToken'] != '0x0000000000000000000000000000000000000000'):
        token = Contract.from_abi("Token", address=values['tiers'][tierID]['depositToken'], abi=Token.abi, owner=acct)
        checkAllowance(token, origins.address, amount)
    origins.buy(tierID, amount, {'value':rbtcAmount})

# =========================================================================================================================================
def addMyselfAsVerifier():
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)
    print("\nAdding myself as a Verifier...")
    origins.addVerifier(acct)
    print("Added",acct,"as a verifier.")

# =========================================================================================================================================
def verifyWallet():
    tierID = readTier("add the wallet list to")
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)
    origins.multipleAddressSingleTierVerification(values['toVerify'], tierID)
    print("All the address Verified.")

# =========================================================================================================================================
def removeMyselfAsVerifier():
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)
    print("\nRemoving myself as a Verifier...")
    origins.removeVerifier(acct)
    print("Removed myself as a Verifier.")

# =========================================================================================================================================
def removeMyselfAsOwner():
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)
    print("\nRemoving myself as an Owner...")
    origins.removeOwner(acct)
    print("Removed myself as an Owner.")

# =========================================================================================================================================
def getTierCount():
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)
    print("\n=============================================================")
    print("Tier Count:",origins.getTierCount())
    print("=============================================================")

# =========================================================================================================================================
def getTierDetails():
    # Here +1 is added because readTier will return 0 for entering 1. The index in Smart Contract is 1 itself, unlike the JSON file.
    tierID = readTier("read")
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)

    minAmount, maxAmount, remainingTokens, saleStartTimestamp, saleEnd, unlockedTS, unlockedBP, vestOrLockCliff, vestOrLockDuration, depositRate = origins.readTierPartA(tierID)
    depositToken, depositType, verificationType, saleEndDurationOrTimestamp, transferType = origins.readTierPartB(tierID)

    decimal = int(values['decimal'])
    tokensForSale = remainingTokens / (10 ** decimal)
    depositTypeReadable = getDepositType(int(depositType))
    verificationTypeReadable = getVerificationType(int(verificationType))
    saleEndDurationOrTimestampReadable = getSaleEndDurationOrTS(int(saleEndDurationOrTimestamp))
    transferTypeReadable = getTransferType(int(transferType))

    print("\n=============================================================")
    print("Tier Details of Tier ID",tierID)
    print("=============================================================")
    print("Minimum allowed asset:               ", minAmount)
    print("Maximum allowed asset:               ", maxAmount)
    print("Tokens For Sale (with Decimal):      ", tokensForSale)
    print("Tokens For Sale (without Decimal):   ", remainingTokens)
    print("Sale Start Timestamp:                ", saleStartTimestamp)
    print("Sale End Duration/Timestamp:         ", saleEnd)
    # print("Unlocked Token Timestamp:            ", unlockedTS)
    print("Unlocked Token Basis Point:          ", unlockedBP)
    print("Vest Or Lock Cliff:                  ", vestOrLockCliff)
    print("Vest Or Lock Duration:               ", vestOrLockDuration)
    print("Deposit Rate:                        ", depositRate)
    print("Deposit Token:                       ", depositToken)
    print("Deposit Type:                        ", depositTypeReadable)
    print("Verification Type:                   ", verificationTypeReadable)
    print("Sale End Duration or Timestamp:      ", saleEndDurationOrTimestampReadable)
    print("Transfer Type:                       ", transferTypeReadable)
    print("=============================================================")

# =========================================================================================================================================
def getOwnerList():
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)
    print("\n=============================================================")
    print("Owner List: ",origins.getOwners())
    print("=============================================================")

# =========================================================================================================================================
def getVerifierList():
    origins = Contract.from_abi("OriginsBase", address=values['origins'], abi=OriginsBase.abi, owner=acct)
    print("\n=============================================================")
    print("Verifier List: ",origins.getVerifiers())
    print("=============================================================")

# =========================================================================================================================================
def writeToJSON():
    if thisNetwork == "development":
        fileHandle = open('./scripts/values/development.json', "w")
    elif thisNetwork == "testnet" or thisNetwork == "rsk-testnet":
        fileHandle = open('./scripts/values/testnet.json', "w")
    elif thisNetwork == "rsk-mainnet":
        fileHandle = open('./scripts/values/mainnet.json', "w")
    json.dump(values, fileHandle, indent=4)

# =========================================================================================================================================
def waitTime():
    if(thisNetwork != "development"):
        print("\nWaiting for 30 seconds for the node to propogate correctly...\n")
        time.sleep(15)
        print("Just 15 more seconds...\n")
        time.sleep(10)
        print("5 more seconds I promise...\n")
        time.sleep(5)
