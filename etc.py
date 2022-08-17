#!/usr/bin/python3
import re
import json
from web3 import Web3
import time
import abi as key
import esett as set
import argparse
import sys
import requests
import threading
from decimal import Decimal
from subprocess import call
import multiprocessing

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--a", help="Token address")
parser.add_argument("-g", "--g", help="Costum Gwei")
parser.add_argument("-gs", "--gs", help="Costum Gwei for Sell")
parser.add_argument("-ga", "--ga", help="Costum Gwei for Approve")
parser.add_argument("-gas", "--gas", help="Costum Gas limit, l for low 350k, m for medium 900k, h for high 3M")
parser.add_argument("-n", "--n", help="Amount of ETH you want to spend")
parser.add_argument("-sapr", "--sapr", action="store_true", help="Disable Approve Token")
parser.add_argument("-aprc", "--aprc", action="store_true", help="Check Approve Token")
parser.add_argument("-apr", "--apr", action="store_true", help="Approve Token")
parser.add_argument("-rvk", "--rvk", action="store_true", help="Revoke Token")
parser.add_argument("-ws", "--ws", action="store_true", help="Watch & Sell")
parser.add_argument("-was", "--was", action="store_true", help="Wait Tax drop and Sell")
parser.add_argument("-bo", "--bo", action="store_true", help="Buy Only")
parser.add_argument("-so", "--so", action="store_true", help="Sell Only")
parser.add_argument("-bf", "--bf", help="Buy For / Costum Recipient")
parser.add_argument("-cs", "--cs", help="Costum Amount of sell")
parser.add_argument("-csp", "--csp", help="Costum Amount of sell in percent")
parser.add_argument("-mb", "--mb", help="Multi Buy")
parser.add_argument("-tod", "--tod", action="store_true", help="Disable Token Info")
parser.add_argument("-s", "--s", help="Splippage (Only for Max buy")
parser.add_argument("-ma", "--ma", action="store_true", help="Multi account")
parser.add_argument("-ak", "--ak", help="Select which account to use eg: -ak 2 (Second account) etc")
parser.add_argument('-stdbuy', "--stdbuy", action="store_true", help="Std Buy: swapExactETCForTokens")
parser.add_argument('-mx', "--mx", help="set max buy in percent")
parser.add_argument("-pr", "--pr", help="Select Your Pair eg: -pr bnb , -pr -busd , -pr usdt , -pr usdc")
parser.add_argument("-m1", "--m1", action="store_true", help="Costum Max Tx. PAUSE MODE")
parser.add_argument("-m2", "--m2", action="store_true", help="Costum Max Tx. AUTO MODE")
parser.add_argument("-m3", "--m3", action="store_true", help="Max Tx Exact Amount token . PAUSE MODE")
parser.add_argument("-m4", "--m4", action="store_true", help="Max Tx Exact Amount token . AUTO MODE")
parser.add_argument("-sp", "--sp", action="store_true", help="Sniperbot Mode")
parser.add_argument("-slp", "--slp", help="Slippage")
parser.add_argument("-c", "--c", action="store_true", help="Sniperbot Check Mode")
parser.add_argument("-t", "--t", action="store_true", help="Help you measure node speed")
parser.add_argument("-d", "--d", help="Skip Deadblock eg: -d 2 (You will skip 2 blocks)")
parser.add_argument("-tp", "--tp", help="Take Profit eg: -tp 200 (Automatic sell when get 200 percents profit )")

args = parser.parse_args()

#select which account to use
if args.ak == None:
    #account list for loop
    akuns = [set.account[0]]
    #singleaccounwithoutlist
    akunn = set.account[0]
    recipient = [set.account[0]]
    privatekeyss = [set.private[0]]
    #privatekeywithoutlist
    privatekeysn = set.private[0]
if args.ak != None:
    if args.ak.isdigit() == True:
    #account list for loop 
        akuns = [set.account[int(args.ak)-1]]
    #singaccounwithoutlist
        akunn = set.account[int(args.ak)-1]
        recipient = [set.account[int(args.ak)-1]]
        privatekeyss = [set.private[int(args.ak)-1]]
    #privatekeywithoutlist
        privatekeysn = set.private[int(args.ak)-1]
    if ',' in args.ak:
        a = (re.findall(r"(\d+),", args.ak))
        b = (re.findall(r",(\d+)", args.ak))
        a = a[0]
        b = b[0]
#buy for
if args.bf != None:
    recipient = [args.bf]
#multiwallet
if args.ma == True:
    akuns = set.account
    recipient = set.account
    privatekeyss = set.private
#multibuy   
if args.mb == None: 
    mb = 1
else: 
    mb = args.mb
#bau
akunz = set.account



class SniperBot():

    def __init__(self):
        self.w3 = self.node()
        self.parseArgs()
          
    def node(self):
        nodes = set.nodes
        if bool(nodes) == False:
            print('Please input RPC/WSS url first!')
            sys.exit()
        if 'http' in nodes:
            w3 = Web3(Web3.HTTPProvider(nodes))
        else:
            w3 = Web3(Web3.WebsocketProvider(nodes))
        return w3

    def Welcome(self):
        if args.c == True:
            print("---------------------------------")
            pass
        else:
            print("---------------------------------")
            print(key.CYELLOW+"Amount :"+key.RESET+'\n'+ str(self.amount) + str(self.symbols))
            print(key.CYELLOW+"Contract Address :"+key.RESET+'\n'+str(self.token))
        
    def parseArgs(self):
        self.token = self.w3.toChecksumAddress(self.shit())
        self.amount = self.nominal()
        self.amountForSnipe = float(self.amount)
        self.gas = self.gass()
        self.symbols =  self.symbols()

    def gass(self):
        gass =  set.gas
        if args.gas == None:
            gass =  set.gas
        if args.gas == 'l' or args.gas == 'L':
            gass = 350000
        if args.gas == 'm' or args.gas == 'M':
            gass = 900000
        if args.gas == 'h' or args.gas == 'H':
            gass = 3000000        
        return gass
    
    def shit(self):
        shit = args.a
        if bool(args.a) == False:
            print(key.CVIOLET +'###########################################################'+key.RESET)
            print(key.CRED +'Enter Contract Address:'+key.RESET)
            token = input().lower()
            remletter = token.replace('zero', '0').replace('one', '1').replace('two', '2').replace('three', '3').replace('four', '4').replace('five', '5').replace('six', '6').replace('seven', '7').replace('eight', '8').replace('nine', '9').replace('ten', '10').replace('eleven', '11').replace('twelve', '12').replace('thirteen', '13').replace('fourteen', '14').replace('fifteen', '15').replace('sixteen', '16').replace('seventeen', '17').replace('eighteen', '18').replace('nineteen', '19').replace('twenty', '20').replace('remove', '').replace('delete', '').replace('beginning', '').replace('middle', '').replace('end', '').replace('first', '').replace('second', '').replace('third', '').replace('space', '').replace('part', '')
            shit = remletter
            efirst = r"(\([0-9][^a-zA-Z0-9_][0-9]\))"
            matches = re.findall(efirst, shit)
            for i in range(0,len(matches)):
                if bool(matches) == True:
                    efirst = r"(\([0-9][^a-zA-Z0-9_][0-9]\))"
                    matches = re.findall(efirst, shit)
                    rem = matches[0].replace('(', '').replace(')', '')
                    conint = eval(rem)
                    jst = shit.replace(str(matches[0]),str(conint))
                    shit = jst
                else:
                    shit = remletter
            wtext = re.sub(r'[^a-zA-Z0-9]','',shit)
            shit = wtext
        else:
            shit = args.a
        return shit


    def nominal(self):
        nom1 = set.nonimal1
        nom2 = args.n
        if nom2 == None:
            nominal = nom1
        else: 
            nominal = nom2
        return nominal
    
    def spairs(self):
        if args.pr == None:
            spairs = '0x82A618305706B14e7bcf2592D4B9324A366b6dAd'#wbnb
        if args.pr == 'busd':
            spairs = '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56'#busd
        if args.pr == 'usdt':
            spairs = '0xE411107D661f722598B4956820292dc82eD1507C'#usdt
        if args.pr == 'usdc':
            spairs = '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d'#usdc
        return spairs

    def pairs_factory(self):
        pairs_address = self.spairs()
        pairs_address_abi = key.pairs_abi
        pairs_factory = self.w3.eth.contract(address=pairs_address, abi=pairs_address_abi)
        return pairs_factory
    
    def symbols(self):
        symbolsr = self.pairs_factory().functions.symbol().call()
        symbols = symbolsr.replace('W', '')
        return symbols
    
    def gwei(self):
        #gwei
        gwei1 = set.gwei1
        gwei2 = args.g
        if gwei2 == None:
            gwei = gwei1
        else:
            gwei = gwei2
        #gweisell/send
        gweis1 = set.gsell
        gweis2 = args.gs
        if gweis2 == None:
            gweis = gweis1
        else:
            gweis = gweis2
        #gwei approve
        gweia1 = set.gaprv
        gweia2 = args.ga
        if gweia2 == None:
            gweia = gweia1
        else:
            gweia = gweia2
        return gwei, gweis, gweia
    
    def pancake_factory(self):
        pancake_factory_address = '0x09fafa5eecbc11C3e5d30369e51B7D9aab2f3F53'
        pancake_factory_abi = key.pancake_factory_abi
        pancake_factory = self.w3.eth.contract(address=pancake_factory_address, abi=pancake_factory_abi)
        return pancake_factory

    def prouter(self):
        pancake_router_address = '0xEcBcF5C7aF4c323947CFE982940BA7c9fd207e2b'
        pancake_router_abi = key.pancake_router_abi
        prouter = self.w3.eth.contract(address=pancake_router_address, abi=pancake_router_abi)
        return prouter, pancake_router_address

    def pairs(self):
        token1 = self.spairs()
        token2 = self.token
        none = '0x0000000000000000000000000000000000000000'
        check_pairs = self.pancake_factory().functions.getPair(token1,token2).call()
        if check_pairs == none:
            print(key.CBLUE + 'Cheking Pair Please Wait.....'+key.RESET+'\n'+key.CGREEN + 'Pair Not Detected '+'\n'+key.RESET+key.CVIOLET+'Waiting Pairs !'+key.RESET)
            while True:
                try:
                    check_pairs = self.pancake_factory().functions.getPair(token1,token2).call()
                    if check_pairs != none:
                        break
                except Exception as e:
                    if 'HTTPError' in str(e):
                        print('Seems like your request has been limited by your node'+'\n'+'If this keeps happening change your node')
                        time.sleep(2)
                        continue
                except KeyboardInterrupt:
                    sys.exit()
                
        check_pairs = check_pairs
        checkLP = self.pairs_factory().functions.balanceOf(check_pairs).call()
        TotalLP = self.w3.fromWei(checkLP,'ether')
        if TotalLP < set.minLP:
            print(key.CRED + 'Liquadity Not Detected '+'\n'+key.RESET+key.CVIOLET+'Waiting Dev Add The Liquadity !'+key.RESET)
            while True:
                try:
                    check_pairs = check_pairs
                    checkLP = self.pairs_factory().functions.balanceOf(check_pairs).call()
                    TotalLP = self.w3.fromWei(checkLP,'ether')
                    if TotalLP > set.minLP:
                        break
                except Exception as e:
                    if 'HTTPError' in str(e):
                        print('Seems like your request has been limited by your node'+'\n'+'If this keeps happening change your node')
                        time.sleep(2)
                        continue
                except KeyboardInterrupt:
                    sys.exit() 
        print(key.CGREEN + 'Liquadity is Detected '+'\n'+key.RESET+str(TotalLP) +key.CYELLOW+' '+str(self.symbols)+key.RESET+'\n'+key.CRED+'Checking Trade Status !'+key.RESET)

    def sell_contract(self):
        sell_router = self.w3.toChecksumAddress(self.token) 
        sell_router_abi = key.sellAbi
        sell_contract = self.w3.eth.contract(sell_router, abi=sell_router_abi)
        return sell_contract
    
    #get token_decimals
    def getdecimals(self):
        getdecimals = self.sell_contract().functions.decimals().call()
        return getdecimals
    
    def tokinfo(self):
        if args.c == True:
            if args.tod == False:
                #tokenname
                tokname = 'None'
                try:
                    calltokname = self.sell_contract().functions.name().call()
                    if bool(calltokname) == True:
                        tokname = calltokname
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                #tokendecimals
                tokdecimals = 0
                try:
                    calltokdecimals = self.sell_contract().functions.decimals().call()
                    if calltokdecimals == int(calltokdecimals):
                        tokdecimals = calltokdecimals
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                #tokensymbol
                toksysmbl = 'None'
                try:
                    calltoksysmbl = self.sell_contract().functions.symbol().call()
                    if calltoksysmbl == str(calltoksysmbl):
                        toksysmbl = calltoksysmbl
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                #totalsupply
                toksupply = 0
                try:
                    calltoksupply = int((self.sell_contract().functions.totalSupply().call()) / (10**tokdecimals))
                    if calltoksupply == int(calltoksupply):
                        toksupply = calltoksupply
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                #maxbuy
                tokmaxtx = 0
                mxtxinper = 0
                tokmaxinbnb = 0
                try:
                    calltokmaxtx = int((self.sell_contract().functions._maxTxAmount().call()) / (10**tokdecimals))
                    if calltokmaxtx == int(calltokmaxtx):
                        tokmaxtx = calltokmaxtx
                        mxtxinper = float(tokmaxtx) / float(float(toksupply) / float(100))
                        tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(self.sell_contract().functions._maxTxAmount().call()),[self.token, self.spairs()]).call()
                        tokmaxinbnb = self.w3.fromWei(tokmaxinbnb[1],'ether')
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try:
                    calltokmaxtx = int((self.sell_contract().functions.maxBuyAmount().call()) / (10**tokdecimals))
                    if calltokmaxtx == int(calltokmaxtx):
                        tokmaxtx = calltokmaxtx
                        mxtxinper = float(tokmaxtx) / float(float(toksupply) / float(100))
                        tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(self.sell_contract().functions.maxBuyAmount().call()),[self.token, self.spairs()]).call()
                        tokmaxinbnb = self.w3.fromWei(tokmaxinbnb[1],'ether')
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try:
                    calltokmaxtx = int((self.sell_contract().functions.maxTxAmount().call()) / (10**tokdecimals))
                    if calltokmaxtx == int(calltokmaxtx):
                        tokmaxtx = calltokmaxtx
                        mxtxinper = float(tokmaxtx) / float(float(toksupply) / float(100))
                        tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(self.sell_contract().functions.maxTxAmount().call()),[self.token, self.spairs()]).call()
                        tokmaxinbnb = self.w3.fromWei(tokmaxinbnb[1],'ether')
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try:
                    calltokmaxtx = int((self.sell_contract().functions.maxTxAmountBuy().call()) / (10**tokdecimals))
                    if calltokmaxtx == int(calltokmaxtx):
                        tokmaxtx = calltokmaxtx
                        mxtxinper = float(tokmaxtx) / float(float(toksupply) / float(100))
                        tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(self.sell_contract().functions.maxTxAmountBuy().call()),[self.token, self.spairs()]).call()
                        tokmaxinbnb = self.w3.fromWei(tokmaxinbnb[1],'ether')
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try:
                    calltokmaxtx = int((self.sell_contract().functions.maxBuyLimit().call()) / (10**tokdecimals))
                    if calltokmaxtx == int(calltokmaxtx):
                        tokmaxtx = calltokmaxtx
                        mxtxinper = float(tokmaxtx) / float(float(toksupply) / float(100))
                        tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(self.sell_contract().functions.maxBuyLimit().call()),[self.token, self.spairs()]).call()
                        tokmaxinbnb = self.w3.fromWei(tokmaxinbnb[1],'ether')
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try:
                    calltokmaxtx = int((self.sell_contract().functions._maxBuy().call()) / (10**tokdecimals))
                    if calltokmaxtx == int(calltokmaxtx):
                        tokmaxtx = calltokmaxtx
                        mxtxinper = float(tokmaxtx) / float(float(toksupply) / float(100))
                        tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(self.sell_contract().functions._maxBuy().call()),[self.token, self.spairs()]).call()
                        tokmaxinbnb = self.w3.fromWei(tokmaxinbnb[1],'ether')
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try:
                    calltokmaxtx = int((self.sell_contract().functions._maxBuyTxAmount().call()) / (10**tokdecimals))
                    if calltokmaxtx == int(calltokmaxtx):
                        tokmaxtx = calltokmaxtx
                        mxtxinper = float(tokmaxtx) / float(float(toksupply) / float(100))
                        tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(self.sell_contract().functions._maxBuyTxAmount().call()),[self.token, self.spairs()]).call()
                        tokmaxinbnb = self.w3.fromWei(tokmaxinbnb[1],'ether')
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try:
                    calltokmaxtx = int((self.sell_contract().functions.checkMaxTxAmount().call()) / (10**tokdecimals))
                    if calltokmaxtx == int(calltokmaxtx):
                        tokmaxtx = calltokmaxtx
                        mxtxinper = float(tokmaxtx) / float(float(toksupply) / float(100))
                        tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(self.sell_contract().functions.checkMaxTxAmount().call()),[self.token, self.spairs()]).call()
                        tokmaxinbnb = self.w3.fromWei(tokmaxinbnb[1],'ether')
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try:
                    calltokmaxtx = int((self.sell_contract().functions._getMaxTxAmount().call()) / (10**tokdecimals))
                    if calltokmaxtx == int(calltokmaxtx):
                        tokmaxtx = calltokmaxtx
                        mxtxinper = float(tokmaxtx) / float(float(toksupply) / float(100))
                        tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(self.sell_contract().functions._getMaxTxAmount().call()),[self.token, self.spairs()]).call()
                        tokmaxinbnb = self.w3.fromWei(tokmaxinbnb[1],'ether')
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try:
                    calltokmaxtx = int((self.sell_contract().functions.sellLimit().call()) / (10**tokdecimals))
                    if calltokmaxtx == int(calltokmaxtx):
                        tokmaxtx = calltokmaxtx
                        mxtxinper = float(tokmaxtx) / float(float(toksupply) / float(100))
                        tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(self.sell_contract().functions.sellLimit().call()),[self.token, self.spairs()]).call()
                        tokmaxinbnb = self.w3.fromWei(tokmaxinbnb[1],'ether')
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try:
                    calltokmaxtx = int((self.sell_contract().functions.maxTransactionAmount().call()) / (10**tokdecimals))
                    if calltokmaxtx == int(calltokmaxtx):
                        tokmaxtx = calltokmaxtx
                        mxtxinper = float(tokmaxtx) / float(float(toksupply) / float(100))
                        tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(self.sell_contract().functions.maxTransactionAmount().call()),[self.token, self.spairs()]).call()
                        tokmaxinbnb = self.w3.fromWei(tokmaxinbnb[1],'ether')
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                #maxsell
                tokmaxsl = 0
                mxslinper = 0
                try: 
                    calltokmaxsl = int((self.sell_contract().functions.maxSellAmount().call()) / (10**tokdecimals))
                    if calltokmaxsl == int(calltokmaxsl):
                        tokmaxsl = calltokmaxsl
                        mxslinper = float(tokmaxsl) / float(float(toksupply) / float(100))
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try: 
                    calltokmaxsl = int((self.sell_contract().functions.maxSellLimit().call()) / (10**tokdecimals))
                    if calltokmaxsl == int(calltokmaxsl):
                        tokmaxsl = calltokmaxsl
                        mxslinper = float(tokmaxsl) / float(float(toksupply) / float(100))
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                #maxwallet
                tokmaxwl = 0
                mxwlinpr = 0
                maxwlinbnb = 0
                try: 
                    calltokmaxwl = int((self.sell_contract().functions._walletMax().call()) / (10**tokdecimals))
                    if calltokmaxwl == int(calltokmaxwl):
                        tokmaxwl = calltokmaxwl
                        mxwlinpr = float(tokmaxwl) / float(float(toksupply) / float(100))
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try: 
                    calltokmaxwl = int((self.sell_contract().functions.maxWalletSize().call()) / (10**tokdecimals))
                    if calltokmaxwl == int(calltokmaxwl):
                        tokmaxwl = calltokmaxwl
                        mxwlinpr = float(tokmaxwl) / float(float(toksupply) / float(100))
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try: 
                    calltokmaxwl = int((self.sell_contract().functions._maxWalletToken().call()) / (10**tokdecimals))
                    if calltokmaxwl == int(calltokmaxwl):
                        tokmaxwl = calltokmaxwl
                        mxwlinpr = float(tokmaxwl) / float(float(toksupply) / float(100))
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try: 
                    calltokmaxwl = int((self.sell_contract().functions._maxWalletAmount().call()) / (10**tokdecimals))
                    if calltokmaxwl == int(calltokmaxwl):
                        tokmaxwl = calltokmaxwl
                        mxwlinpr = float(tokmaxwl) / float(float(toksupply) / float(100))
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try: 
                    calltokmaxwl = int((self.sell_contract().functions.maxWalletLimit().call()) / (10**tokdecimals))
                    if calltokmaxwl == int(calltokmaxwl):
                        tokmaxwl = calltokmaxwl
                        mxwlinpr = float(tokmaxwl) / float(float(toksupply) / float(100))
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try: 
                    calltokmaxwl = int((self.sell_contract().functions.checkMaxWalletToken().call()) / (10**tokdecimals))
                    if calltokmaxwl == int(calltokmaxwl):
                        tokmaxwl = calltokmaxwl
                        mxwlinpr = float(tokmaxwl) / float(float(toksupply) / float(100))
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try: 
                    calltokmaxwl = int((self.sell_contract().functions.maxWallet().call()) / (10**tokdecimals))
                    if calltokmaxwl == int(calltokmaxwl):
                        tokmaxwl = calltokmaxwl
                        mxwlinpr = float(tokmaxwl) / float(float(toksupply) / float(100))
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                #tokenbalance
                tokbal = 0
                kokbalint = 0
                try: 
                    calltokbal = self.sell_contract().functions.balanceOf(akunn).call()
                    if calltokbal == int(calltokbal):
                        tokbal = calltokbal
                        kokbalint = int((tokbal) / (10**tokdecimals))
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                try: 
                    calltokmaxwl = int((self.sell_contract().functions._maxWalletSize().call()) / (10**tokdecimals))
                    if calltokmaxwl == int(calltokmaxwl):
                        tokmaxwl = calltokmaxwl
                        mxwlinpr = float(tokmaxwl) / float(float(toksupply) / float(100))
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                print('*Token Informations*'+'\n'+'---------------------------------'+'\n'+'Name : '+str(tokname)+'\n'+'Decimals : '+str(tokdecimals)+'\n'+'Symbol : '+str(toksysmbl)+'\n'+'Total Supply : '+str(toksupply)+'\n'+'MaxTx : '+str(tokmaxtx)+' / '+str(mxtxinper)+'%'+' / '+str(tokmaxinbnb)+' '+str(self.symbols)+'\n'+'Max_Sell : '+str(tokmaxsl)+' / '+str(mxslinper)+'%'+'\n'+'Max_Wallet : '+str(tokmaxwl)+' / '+str(mxwlinpr)+'%'+'\n'+'Token Balance : '+str(kokbalint)+'\n'+'---------------------------------')
            else:
                pass
        else:
            pass
    
    #maxtx
    def maxtx(self):
        maxtx = 0
        if args.m1 == True or args.m2 == True:
            toksupply = self.sell_contract().functions.totalSupply().call()
            if args.mx == None:
                cmax = 1
            if args.mx != None:
                cmax = args.mx
            maxtx =  int(float(toksupply / 100 * float(cmax)))
        if args.m3 == True or args.m4 == True:
            try:
                maxtx = self.sell_contract().functions.checkMaxTxAmount().call()
                if maxtx.isdigit() == True:
                    maxtx = int(maxtx)
            except Exception as e:
                if 'execution reverted' in str(e):
                    pass
            try: 
                maxtx = self.sell_contract().functions._maxTxAmount().call()
                if maxtx.isdigit() == True:
                    maxtx = int(maxtx)
            except Exception as e:
                if 'execution reverted' in str(e):
                    pass
            try: 
                maxtx = self.sell_contract().functions.maxBuyAmount().call()
                if maxtx.isdigit() == True:
                    maxtx = int(maxtx)
            except Exception as e:
                if 'execution reverted' in str(e):
                    pass
            try: 
                maxtx = self.sell_contract().functions.maxTxAmount().call()
                if maxtx.isdigit() == True:
                    maxtx = int(maxtx)
            except Exception as e:
                if 'execution reverted' in str(e):
                    pass
            try: 
                maxtx = self.sell_contract().functions.maxTxAmountBuy().call()
                if maxtx.isdigit() == True:
                    maxtx = int(maxtx)
            except Exception as e:
                if 'execution reverted' in str(e):
                    pass
            try: 
                maxtx = self.sell_contract().functions.maxBuyLimit().call()
                if maxtx.isdigit() == True:
                    maxtx = int(maxtx)
            except Exception as e:
                if 'execution reverted' in str(e):
                    pass
            try: 
                maxtx = self.sell_contract().functions._maxBuy().call()
                if maxtx.isdigit() == True:
                    maxtx = int(maxtx)
            except Exception as e:
                if 'execution reverted' in str(e):
                    pass
            try:
                maxtx = self.sell_contract().functions._maxBuyTxAmount().call()
                if maxtx.isdigit() == True:
                    maxtx = int(maxtx)
            except Exception as e:
                if 'execution reverted' in str(e):
                    pass
            try:
                maxtx = self.sell_contract().functions._getMaxTxAmount().call()
                if maxtx.isdigit() == True:
                    maxtx = int(maxtx)
            except Exception as e:
                if 'execution reverted' in str(e):
                    pass
            try:
                maxtx = self.sell_contract().functions.sellLimit().call()
                if maxtx.isdigit() == True:
                    maxtx = int(maxtx)
            except Exception as e:
                if 'execution reverted' in str(e):
                    pass
            try:
                maxtx = self.sell_contract().functions.maxTransactionAmount().call()
                if maxtx.isdigit() == True:
                    maxtx = int(maxtx)
            except Exception as e:
                if 'execution reverted' in str(e):
                    pass  
        return maxtx

    def maxinether(self):
        maxtx = self.maxtx()
        if maxtx == 0:
            print(key.CRED +'There is No Max transactions !'+key.RESET)
            sys.exit()
        else:
            pass
        tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(maxtx),[self.token, self.spairs()]).call()
        tokmaxinbnb = self.w3.fromWei(tokmaxinbnb[1],'ether')
        print('---------------------------------'+'\n'+'Max tx Pause Mode'+'\n'+'---------------------------------'+'\n'+'Max tx in BNB:')
        def loop():
            stop = False
            def normal():
                nonlocal stop
                while True:
                    try:
                        tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(maxtx),[self.token, self.spairs()]).call()
                        tokmaxinbnb = self.w3.fromWei(tokmaxinbnb[1],'ether')
                        print(str(tokmaxinbnb), end='\r')
                        if stop == True:
                            break

                    except KeyboardInterrupt:
                        sys.exit()

                    except Exception as e:
                        if 'execution reverted' in str(e):
                            continue
                normal = tokmaxinbnb
                return normal

            def get_input():
                nonlocal stop
                keystrk = input()
                stop = True
            n = threading.Thread(target=normal)
            i = threading.Thread(target=get_input) 
            n.start()
            i.start()
            n.join()
            i.join()
        loop()

    def maxinetherauto(self):
        maxtx = self.maxtx()
        if maxtx == 0:
            print(key.CRED +'There is No Max transactions !'+key.RESET)
            sys.exit()
        else:
            pass
        tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(maxtx),[self.token, self.spairs()]).call()
        tokmaxinbnb = self.w3.fromWei(tokmaxinbnb[1],'ether')
        maxinetherauto = tokmaxinbnb
        return maxinetherauto
    
        
    #buy token    
    def buystd(self):
        #gwei
        gwei = self.gwei()[0]
        #amountbuy######
        nominal = self.nominal()
        #Buying
        print(key.CVIOLET +'Buying Token'+key.RESET)
        #Buy Token with BNB and MaxBuy
        if args.stdbuy == False:
            buys = self.prouter()[0].functions.swapExactETCForTokens
            amountinout = 0
            if args.slp == None:
                amountinout = 0
            if args.slp != None:
                sp = args.slp
                getprice = float(self.nominal()) * int(10**18)
                minreceive = self.prouter()[0].functions.getAmountsOut(int(getprice),[self.spairs(), self.token]).call()
                amountinout = int(minreceive[1] - (minreceive[1]/100*int(sp)))
            nominal = self.nominal()
        if args.m1 == True:
            self.maxinether()
            buys = self.prouter()[0].functions.swapETCForExactTokens
            amountinout = self.maxtx()
            tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(amountinout),[self.token, self.spairs()]).call()
            nominal = self.w3.fromWei(tokmaxinbnb[1],'ether')
            spmx = set.spmx
            if args.s != None:
                spmx = int(args.s)
            if args.s == None:
                spmx = set.spmx
            if args.n == None:
                nominal = (nominal + (nominal / 100 * spmx))
            if args.n != None:
                nominal = args.n
            nominal = nominal
        
        if args.m2 == True:
            buys = self.prouter()[0].functions.swapETCForExactTokens
            amountinout = self.maxtx()
            nominal = self.maxinetherauto()
            spmx = set.spmx
            if args.s != None:
                spmx = int(args.s)
            if args.s == None:
                spmx = set.spmx
            if args.n == None:
                nominal = (nominal + (nominal / 100 * spmx))
            if args.n != None:
                nominal = args.n
            nominal = nominal

        if args.m3 == True:
            self.maxinether()
            buys = self.prouter()[0].functions.swapETCForExactTokens
            amountinout = self.maxtx()
            tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(amountinout),[self.token, self.spairs()]).call()
            nominal = self.w3.fromWei(tokmaxinbnb[1],'ether')
            spmx = set.spmx
            if args.s != None:
                spmx = int(args.s)
            if args.s == None:
                spmx = set.spmx
            if args.n == None:
                nominal = (nominal + (nominal / 100 * spmx))
            if args.n != None:
                nominal = args.n
            nominal = nominal

        if args.m4 == True:
            buys = self.prouter()[0].functions.swapETCForExactTokens
            amountinout = self.maxtx()
            nominal = self.maxinetherauto()
            spmx = set.spmx
            if args.s != None:
                spmx = int(args.s)
            if args.s == None:
                spmx = set.spmx
            if args.n == None:
                nominal = (nominal + (nominal / 100 * spmx))
            if args.n != None:
                nominal = args.n
            nominal = nominal
               
        #WBNB pair 
        if args.pr == None:
            for i in range(int(mb)):
                #multiaddress
                for i in range(0,len(akuns)):
                    pancakeswap2_txn = buys(
                    int(amountinout),
                    [self.spairs(),self.token],
                    recipient[i],
                    (int(time.time()) + 10000)
                    ).buildTransaction({
                    'from': akuns[i],
                    'value': self.w3.toWei((nominal),'ether'),
                    'gas': self.gas,
                    'gasPrice': self.w3.toWei((gwei),'gwei'),
                    'nonce': self.w3.eth.get_transaction_count(akuns[i],'pending'),
                    })
                    signed_txn = self.w3.eth.account.sign_transaction(pancakeswap2_txn, private_key=privatekeyss[i])
                    tx_token = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                    rs = (self.w3.toHex(tx_token))
                    #checking transaction status
                    print(key.CYELLOW +'https://blockscout.com/etc/mainnet/tx/'+rs+key.RESET)

        else:
        #USDT & BUSD pairs
            self.approve_pairs()
            for i in range(int(mb)):
                #multiaddress
                #amount
                amountb = (int(nominal) * int(10**18))
                for i in range(0,len(akuns)):
                    pancakeswap2_txn = self.prouter()[0].functions.swapExactTokensForETC(
                    amountb,
                    int(amountinout),
                    [self.spairs(),self.token],
                    recipient[i],
                    (int(time.time()) + 10000)
                    ).buildTransaction({
                    'from': akuns[i],
                    'gas': self.gas,
                    'gasPrice': self.w3.toWei((gwei),'gwei'),
                    'nonce': self.w3.eth.get_transaction_count(akuns[i],'pending'),
                    })
                    signed_txn = self.w3.eth.account.sign_transaction(pancakeswap2_txn, private_key=privatekeyss[i])
                    tx_token = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                    rs = (self.w3.toHex(tx_token))
                    #checking transaction status
                    print(key.CYELLOW +'https://blockscout.com/etc/mainnet/tx/'+rs+key.RESET)
        
        resi = self.w3.eth.wait_for_transaction_receipt(rs)
        block = resi['status']
        if block == 1:
            print(key.CGREEN+'Transaction Succesfull'+key.RESET+'\n'+key.CBLUE +'---------------------------------'+key.RESET)
        if block == 0:
            print(key.CRED+'Transaction Failed'+key.RESET)
            sys.exit()
        #buy for and Buy Only
        if args.bf !=  None or args.bo == True:
            sys.exit()
        
    def notindex(self):
        while True:
            try:
                balance = self.sell_contract().functions.balanceOf(akunn).call()
                if int(balance) == int(0):
                    print(key.CYELLOW+'Please wait while blockchain indexing your transactions...', end='\r'+key.RESET)
                    time.sleep(0.5)
                if int(balance) > int(0):
                    break
            except Exception as e:
                if 'execution reverted' in str(e):
                    continue
    
    def sell(self):
        gwei = self.gwei()[2]
        nominal = self.nominal()
        print(key.CYELLOW +'Checking Token Approve status'+key.RESET)
        if args.sapr == False:
            router_address = self.prouter()
            checkaprv = self.sell_contract().functions.allowance(akunn, router_address[1]).call();
            if checkaprv == 0:
                print(key.CYELLOW +'Approving Token...'+key.RESET)
                approve = self.sell_contract().functions.approve(router_address[1], 115792089237316195423570985008687907853269984665640564039457584007913129639935).buildTransaction({
                    'from': akunn,
                    'gasPrice': self.w3.toWei(gwei,'gwei'),
                    'nonce': self.w3.eth.get_transaction_count(akunn),
                    })
                signed_txn = self.w3.eth.account.sign_transaction(approve, private_key=privatekeysn)
                tx_token2 = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                ar = (self.w3.toHex(tx_token2))
                aresi = self.w3.eth.wait_for_transaction_receipt(ar)
                apr = aresi['status']
                if apr == 1:
                    print(key.CGREEN+'Approved'+key.RESET)
                if apr == 0:
                    print(key.CRED+'Failed'+key.RESET)
                    sys.exit()
            else:
                print(key.CGREEN+'Approved'+key.RESET)
        else:
            print(key.CGREEN+'Approved'+key.RESET)
        
        

        #takeprofit
        if args.tp == None:
            takeprofit = 0
        if args.tp != None:
            takeprofit = args.tp

        if args.so == False:
            if args.ws == False and args.was == False:
                if args.tp != None:
                    totaltp = float(nominal) + float(float(nominal)/float(100)*float(takeprofit))
                    print(key.CYELLOW+'Checking Profit!'+key.RESET)
                    print(key.CRED+'Profit Target '+str(takeprofit)+'% / '+str(totaltp)+' '+str(self.symbols)+key.RESET)
                    self.notindex()
                    while True:
                        try:
                            balance = self.sell_contract().functions.balanceOf(akunn).call()
                            check = self.prouter()[0].functions.getAmountsOut(int(balance),[self.token, self.spairs()]).call()
                            rbnb = self.w3.fromWei(check[1],'ether')
                            totaltp = float(nominal) + float(float(nominal)/float(100)*float(takeprofit))
                            busd = 0
                            try:
                                if args.pr == None:
                                    #profit in busd
                                    busd = '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56'
                                    bcheck = self.prouter()[0].functions.getAmountsOut(int(check[1]),[self.spairs(), busd]).call()
                                    busd = self.w3.fromWei(bcheck[1],'ether')
                            except Exception as e:
                                if 'execution reverted' in str(e):
                                    pass
                            print (key.CYELLOW+'Your Profit: '+key.RESET+key.CGREEN+str(rbnb)+' '+str(self.symbols)+key.RESET+' | ')
                            time.sleep(1)
                            if float(rbnb) > float(totaltp):
                                break
                        except Exception as e:
                            if 'execution reverted' in str(e):
                                time.sleep(0.5)
                                continue
                        except KeyboardInterrupt:
                            break
                if args.tp == None:  
                    print(key.CYELLOW+'Checking Profit!'+key.RESET)
                    self.notindex()
                    while True:
                        try:
                            balance = self.sell_contract().functions.balanceOf(akunn).call()
                            check = self.prouter()[0].functions.getAmountsOut(int(balance),[self.token, self.spairs()]).call()
                            rbnb = self.w3.fromWei(check[1],'ether')
                            print (key.CYELLOW+'Your Profit: '+key.RESET+key.CGREEN+str(rbnb)+' '+str(self.symbols)+key.RESET+' | ')
                            time.sleep(1)
                        except Exception as e:
                            if 'execution reverted' in str(e):
                                time.sleep(0.5)
                                continue
                        except KeyboardInterrupt:
                            break
            else:
                pass
        else:
            if args.was == True:
                self.waitsell()
            else:
                pass

        if args.was == False:
            print(key.CBLUE+'Swapping Token.........'+key.RESET)
        #gwei for sell
        gwei = self.gwei()[1]
        if args.pr == None:
            balance = self.sell_contract().functions.balanceOf(akunn).call()
            if args.cs and args.csp == None:
                balance = self.sell_contract().functions.balanceOf(akunn).call()
            if args.cs != None:
                balance = (int(args.cs) * int(10**self.getdecimals()))
            if args.csp != None:
                balance = ((balance/int(10**self.getdecimals())/100)*int(args.csp)*int(10**self.getdecimals()))
            pancakeswap2_txn = self.prouter()[0].functions.swapExactTokensForETC(
                int(balance),0,
                [self.token, self.spairs()],
                akunn,
                (int(time.time()) + 1000000)
                ).buildTransaction({
                'from': akunn,
                'gas': self.gas,
                'gasPrice': self.w3.toWei((gwei),'gwei'),
                'nonce': self.w3.eth.get_transaction_count(akunn, 'pending'),
                })
            signed_txn = self.w3.eth.account.sign_transaction(pancakeswap2_txn, private_key=privatekeysn)
            tx_token3 = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            jt = (self.w3.toHex(tx_token3))
            print(key.CYELLOW +'https://blockscout.com/etc/mainnet/tx/'+jt+key.RESET)
            jresi = self.w3.eth.wait_for_transaction_receipt(jt)
            jpr = jresi['status']
            if jpr == 1:
                print(key.CGREEN+'Success'+key.RESET)
            if jpr == 0:
                print(key.CRED+'Failed'+key.RESET)
            print(key.CBLUE +'---------------------------------'+key.RESET)
            mbal = self.w3.eth.get_balance(akunn)
            rmbal = self.w3.fromWei(mbal,'ether')
            print('Balance :'+str(rmbal)+key.CYELLOW +' '+str(self.symbols)+key.RESET)
            print(key.CGREEN +'---------------------------------'+key.RESET)
        else:
            #USDT $ BUSD pairs
            balance = self.sell_contract().functions.balanceOf(akunn).call()
            if args.cs and args.csp == None:
                balance = self.sell_contract().functions.balanceOf(akunn).call()
            if args.cs != None:
                balance = (int(args.cs) * int(10**self.getdecimals()))
            if args.csp != None:
                balance = ((balance/int(10**self.getdecimals())/100)*int(args.csp)*int(10**self.getdecimals()))
            pancakeswap2_txn = self.prouter()[0].functions.swapExactTokensForETC(
                int(balance),0,
                [self.token, self.spairs()],
                akunn,
                (int(time.time()) + 10000)
                ).buildTransaction({
                'from': akunn,
                'gas': self.gas,
                'gasPrice': self.w3.toWei((gwei),'gwei'),
                'nonce': self.w3.eth.get_transaction_count(akunn),
                })
            signed_txn = self.w3.eth.account.sign_transaction(pancakeswap2_txn, private_key=privatekeysn)
            tx_token3 = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            jt = (self.w3.toHex(tx_token3))
            print(key.CYELLOW +'https://blockscout.com/etc/mainnet/tx/'+jt+key.RESET)
            jresi = self.w3.eth.wait_for_transaction_receipt(jt)
            jpr = jresi['status']
            if jpr == 1:
                print(key.CGREEN+'Success'+key.RESET)
            if jpr == 0:
                print(key.CRED+'Failed'+key.RESET)
            print(key.CBLUE +'---------------------------------'+key.RESET)
            mbal = self.w3.eth.get_balance(akunn)
            rmbal = self.w3.fromWei(mbal,'ether')
            print('Balance :'+str(rmbal)+key.CYELLOW +' '+str(self.symbols)+key.RESET)
            print(key.CGREEN +'---------------------------------'+key.RESET)
        
        if args.was == True:
            sys.exit()

    def watchsell(self):
        nominal = self.nominal()
        #takeprofit
        if args.tp == None:
            takeprofit = 0
        if args.tp != None:
            takeprofit = args.tp
        #check profit    
        if args.tp != None:
            totaltp = float(nominal) + float(float(nominal)/float(100)*float(takeprofit))
            print(key.CYELLOW+'Checking Profit!'+key.RESET)
            print(key.CRED+'Profit Target '+str(takeprofit)+'% / '+str(totaltp)+' '+str(self.symbols)+key.RESET)
            self.notindex()
            while True:
                try:
                    balance = self.sell_contract().functions.balanceOf(akunn).call()
                    check = self.prouter()[0].functions.getAmountsOut(int(balance),[self.token, self.spairs()]).call()
                    rbnb = self.w3.fromWei(check[1],'ether')
                    totaltp = float(nominal) + float(float(nominal)/float(100)*float(takeprofit))
                    print (key.CYELLOW+'Your Profit: '+key.RESET+key.CGREEN+str(rbnb)+' '+str(self.symbols)+key.RESET+' | ')
                    time.sleep(1)
                    if float(rbnb) > float(totaltp):
                        break
                except Exception as e:
                    if 'execution reverted' in str(e):
                        time.sleep(0.5)
                        continue
                except KeyboardInterrupt:
                    break
        if args.tp == None:  
            print(key.CYELLOW+'Checking Profit!'+key.RESET)
            self.notindex()
            while True:
                try:
                    balance = self.sell_contract().functions.balanceOf(akunn).call()
                    check = self.prouter()[0].functions.getAmountsOut(int(balance),[self.token, self.spairs()]).call()
                    rbnb = self.w3.fromWei(check[1],'ether')
                    print (key.CYELLOW+'Your Profit: '+key.RESET+key.CGREEN+str(rbnb)+' '+str(self.symbols)+key.RESET+' | ')
                    time.sleep(1)
                except Exception as e:
                    if 'execution reverted' in str(e):
                        time.sleep(0.5)
                        continue
                except KeyboardInterrupt:
                    break

    def approvecheck(self):
        router_address = self.prouter()
        checkaprv = self.sell_contract().functions.allowance(akunn, router_address[1]).call();
        if checkaprv == 0:
            print('Token not Approved yet')
        else:
            print('Token Approved Already')

    def approve_pairs(self):
        print(key.CYELLOW +'Checking Pair Approve status'+key.RESET)
        router_address = self.prouter()
        checkaprv = self.pairs_factory().functions.allowance(akunn, router_address[1]).call();
        gwei = self.gwei()[2]
        if args.sapr == False:
            if checkaprv == 0:
                print(key.CYELLOW +'Approving Pair...'+key.RESET)
                tamount = 115792089237316195423570985008687907853269984665640564039457584007913129639935
                approve = self.pairs_factory().functions.approve(router_address[1], int(tamount)).buildTransaction({
                'from': akunn,
                'gasPrice': self.w3.toWei(gwei,'gwei'),
                'nonce': self.w3.eth.get_transaction_count(akunn),
                })
                signed_txn = self.w3.eth.account.sign_transaction(approve, private_key=privatekeysn)
                tx_token2 = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                ar = (self.w3.toHex(tx_token2))
                aresi = self.w3.eth.wait_for_transaction_receipt(ar)
                apr = aresi['status']
                if apr == 1:
                    print(key.CGREEN+'Success'+key.RESET)
                if apr == 0:
                    print(key.CRED+'Failed'+key.RESET)
                    sys.exit()
            else:
                print(key.CGREEN+'Pair Approved'+key.RESET)
        else:
            print(key.CGREEN+'Pair Approved'+key.RESET) 
            

    def approve_revoke(self):
        router_address = self.prouter()
        gwei = self.gwei()[2]
        if args.apr == True:
            print(key.CYELLOW +'Approving Token...'+key.RESET)
            tamount = 115792089237316195423570985008687907853269984665640564039457584007913129639935
        if args.rvk == True:
            print(key.CYELLOW +'Revoking Token...'+key.RESET)
            tamount = 0
        approve = self.sell_contract().functions.approve(router_address[1], int(tamount)).buildTransaction({
            'from': akunn,
            'gasPrice': self.w3.toWei(gwei,'gwei'),
            'nonce': self.w3.eth.get_transaction_count(akunn),
            })
        signed_txn = self.w3.eth.account.sign_transaction(approve, private_key=privatekeysn)
        tx_token2 = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        ar = (self.w3.toHex(tx_token2))
        aresi = self.w3.eth.wait_for_transaction_receipt(ar)
        apr = aresi['status']
        if apr == 1:
            print(key.CGREEN+'Success'+key.RESET)
        if apr == 0:
            print(key.CRED+'Failed'+key.RESET)
            sys.exit()
        print(key.CGREEN+'https://blockscout.com/etc/mainnet/tx/'+ar+key.RESET)
        
    def hpdotio(self):
        response = requests.get(set.honeypotdotio+self.token)
        TokInfo = (response.json())
        Honeypot = TokInfo['IsHoneypot']
        BuyTax = TokInfo['BuyTax']
        SellTax = TokInfo['SellTax']
        MaxTx = TokInfo['MaxTxAmount']
        try:
            if 'NoLiquidity'in TokInfo:
                MaxTx = TokInfo['MaxTxAmount']
            else:
                MaxTx = int(TokInfo['MaxTxAmount'] / (10**self.getdecimals()))
        except Exception as e:
            if 'execution reverted' in str(e):
                pass
        MaxTxinBNB = self.w3.fromWei(TokInfo['MaxTxAmountBNB'], 'ether')
        BuyGas = TokInfo['BuyGas']
        SellGas = TokInfo['SellGas']
        Error = TokInfo['Error']
        return Honeypot, BuyTax, SellTax, MaxTx, MaxTxinBNB, BuyGas, SellGas, Error
    
    def hpdotiorun(self):
        cek1 = self.hpdotio()
        print('---------------------------------'+'\n'+'*honeypot.is*'+'\n'+'---------------------------------'+'\n'+'Error : '+str(cek1[7])+'\n'+'Honeypot : '+str(cek1[0])+'\n'+'BuyTax : '+str(cek1[1])+' %'+'\n'+'SellTax : '+str(cek1[2])+' %'+'\n'+'MaxTx : '+str(cek1[3])+'\n'+'MaxTxinBNB : '+str(cek1[4])+' BNB'+'\n'+'BuyGas : '+str(cek1[5])+'\n'+'SellGas : '+str(cek1[6])+'\n'+'---------------------------------')
        sys.exit()
    
    def hpdotiorunbot(self):
        self.Welcome()
        self.pairs()
        cek1 = self.hpdotio()
        print('---------------------------------'+'\n'+'*honeypot.is*'+'\n'+'---------------------------------'+'\n'+'Error : '+str(cek1[7])+'\n'+'Honeypot : '+str(cek1[0])+'\n'+'BuyTax : '+str(cek1[1])+' %'+'\n'+'SellTax : '+str(cek1[2])+' %'+'\n'+'MaxTx : '+str(cek1[3])+'\n'+'MaxTxinBNB : '+str(cek1[4])+' BNB'+'\n'+'BuyGas : '+str(cek1[5])+'\n'+'SellGas : '+str(cek1[6])+'\n'+'---------------------------------')
        print('Bot Will allow you to buy if tax bellow '+str(set.buytax)+' %'+'\n'+'Waiting Tax and Trade enable !')
        while True:
            if float(cek1[1]) < float(set.buytax):
                break
            #buyandsellaftercheck
        self.buystd()
        self.sell()
        sys.exit()
    
    
    def deadblock(self):
        block = self.w3.eth.blockNumber
        dead1 = set.dead1
        dead2 = args.d
        if dead2 != None and (int(dead2) > int(0)):
                rdead = block+int(dead2)
                dead = rdead
                print(key.CGREEN+'Current block :'+str(block)+key.RESET+'\n'+key.CRED+'Skiping '+dead2+' block'+key.RESET+'\n'+key.CVIOLET+'Buying at block :'+str(rdead)+key.RESET)
                fdead = dead-1
                while True:
                    block = self.w3.eth.blockNumber
                    if block == fdead:
                        break
        if args.d == None:
            pass

    def sniper(self):
        self.Welcome()
        start = time.time()
        if args.c == True:
            self.tokinfo()
        else:
            pass
        if args.m1 == True or args.m2 == True or args.m3 == True or args.m4 == True:
            maxtx = self.maxtx()
            if maxtx == 0:
                print(key.CRED +'There is No Max transactions !'+key.RESET)
                sys.exit()
            else:
                maxtx = self.maxtx()
                toksupply = 0
                try:
                    calltoksupply = int((self.sell_contract().functions.totalSupply().call()) / (10**self.getdecimals()))
                    if calltoksupply == int(calltoksupply):
                        toksupply = calltoksupply
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                maxtxp = int(maxtx / (10**self.getdecimals()))
                mxtxinpr = float(maxtxp) / float(float(toksupply) / float(100))
                tokmaxinbnb = 0
                try:
                    tokmaxinbnb = self.prouter()[0].functions.getAmountsOut(int(maxtx),[self.token, self.spairs()]).call()
                    tokmaxinbnb = self.w3.fromWei(tokmaxinbnb[1],'ether')
                    if type(tokmaxinbnb) == float:
                        pass
                except Exception as e:
                    if 'execution reverted' in str(e):
                        pass
                print('---------------------------------'+'\n'+'MaxTx : '+str(maxtxp)+' / '+str(mxtxinpr)+'%'+' / '+str(tokmaxinbnb)+' '+str(self.symbols))
        self.pairs()
        self.deadblock()
        if args.c == True:
            end = time.time()
            if args.t == True:
                print(end-start, 'Seconds')
                print('Check Mode !'+'\n'+'---------------------------------')
                sys.exit()
            print('Check Mode !'+'\n'+'---------------------------------')
            sys.exit()
        self.buystd()
        self.sell()
        sys.exit()    

    def StartUP(self):
        # self.TXN = TXN(self.token, self.amountForSnipe)
        #approvecheck
        if args.aprc == True:
            self.approvecheck()
            sys.exit()
        #approvetoken
        if args.apr == True:
            self.approve_revoke()
            sys.exit()
        #revoketoken
        if args.rvk == True:
            self.approve_revoke()
            sys.exit()
        #watchsell
        if args.ws == True:
            self.watchsell()
            self.sell()
            sys.exit()
        #sellonly#Waitandsell
        if args.so == True:
            self.sell()
            sys.exit()
        #Sniperbot
        if args.sp == True:
            self.sniper()
        #CheckMode
        if args.c == True:
            self.sniper()
        #buyandsellstd
        self.buystd()
        self.sell()


SniperBot().StartUP()
