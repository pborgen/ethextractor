# Indexer for Ethereum to get transaction list by ETH address
# https://github.com/Adamant-im/ETH-transactions-storage
# By Artem Brunov, Aleksei Lebedev
# 2020-2021 ADAMANT Foundation
# 2017-2020 ADAMANT TECH LABS LP
# v1.2

from operator import truediv
from eth_typing.evm import BlockNumber
from web3 import Web3
from web3.auto import w3
import time
import sys
import logging
import json
#from systemd.journal import JournalHandler

# Get postgre database name


dbname = 'etherium'

# Connect to geth node
#web3 = Web3(Web3.IPCProvider("/home/geth/.ethereum/geth.ipc"))

# Or connect to openethereum node

#web3 = Web3(Web3.IPCProvider("\\\\.\\pipe\\geth.ipc"))
#web3 = Web3(Web3.IPCProvider('https://mainnet.infura.io/v3/6a528c17b68a40b5bc84190aabb81c19'))
web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/6a528c17b68a40b5bc84190aabb81c19'))
#web3 = Web3(Web3.HTTPProvider("http://192.168.1.151:8545"))
# Start logger
logger = logging.getLogger("EthIndexerLog")
logger.setLevel(logging.INFO)

# File logger
lfh = logging.FileHandler("C:/dev/code/ETH-transactions-storage/ethindexer.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
lfh.setFormatter(formatter)
logger.addHandler(lfh)


# Wait for the node to be in sync before indexing
logger.info("Waiting Ethereum node to be in sync...")

#while web3.eth.syncing != False:
    # Change with the time, in second, do you want to wait
    # before cheking again, default is 5 minutes
#    time.sleep(300)
hexContractAddress = '0x2b591e99afe9f32eaa6214f7b7629768c40eeb39'
#bla = web3.eth.filter({'fromBlock': 1000000, 'toBlock': 1000100, 'address': hexContractAddress})
#transaction = web3.eth.get_transaction_receipt('0x93c3e9910efedb739b10d11b891ca03cd4243e9a202099c09a3fb34fd467cd2e');

hex_transaction_example = '0x56a915c7072cbbb6a81dbc994c2d3719b2843415384cd8472d4ba0651ef0414d'



receipt = web3.eth.get_transaction_receipt(hex_transaction_example)

receipt_log_data = receipt['logs'][0]['data']
topics = receipt['logs'][0]['topics'][0]

#json_data = null
with open('E:/tmp/hex_abi.json') as f:
    abi_json = json.load(f)

contract = w3.eth.contract(address=Web3.toChecksumAddress(hexContractAddress), abi=abi_json)


transaction = web3.eth.get_transaction(hex_transaction_example)
func_obj, func_params = contract.decode_function_input(transaction["input"])

abi_events = [abi for abi in contract.abi if abi["type"] == "event"]


receipt_event_signature_hex = web3.toHex(receipt['logs'][0]["topics"][0])

for event in abi_events:
    # Get event signature components
    name = event["name"]
    inputs = [param["type"] for param in event["inputs"]]
    inputs = ",".join(inputs)
    # Hash event signature
    event_signature_text = f"{name}({inputs})"
    event_signature_hex = web3.toHex(web3.keccak(text=event_signature_text))
    # Find match between log's event signature and ABI's event signature
    if event_signature_hex == receipt_event_signature_hex:
        # Decode matching log
        event_name = event['name']
        decoded_logs = contract.events[event_name]().processReceipt(receipt)
        processLog = contract.events[event_name]().processLog(receipt['logs'][0])
        print(decoded_logs)

rich_logs = contract.events.myEvent().processReceipt(receipt)

func_obj, func_params = contract.decode_function_input(receipt_log_data)

web3.eth.abi.decodeParameters(
    [
        {"internalType": "contract MyData","name": "dat","type": "address"},
        {"internalType": "contract Data","name": "_dat","type": "address"}],
        receipt_log_data)

#bla = web3.eth.get_transaction(hex_transaction_example)
print('hello')
for block_number in range(46164, 100000):

    #block = web3.eth.get_block(block_number)
    transaction_count = web3.eth.get_block_transaction_count(block_number)
    if transaction_count > 0:
        for x in range(0, transaction_count):
            transaction = web3.eth.get_transaction_by_block(block_number, x)
            transaction_hash = transaction['hash']
            transaction_transactionIndex = transaction['transactionIndex']
            transaction_blockHash = transaction['blockHash']
            transaction_blocknumber = transaction['blockNumber']
            transaction_value = transaction['value']
            transaction_input = transaction['input']
            transaction_from = transaction['from']
            transaction_to = transaction['to']
            transaction_gasprice = transaction['gasPrice']
            #transaction_maxFeePerGas = transaction['maxFeePerGas']
            #transaction_maxPriortyFeePerGas = transaction['maxPriortyFeePerGas']
            transaction_gas = transaction['gas']

            transaction_receipt = web3.eth.get_transaction_receipt(transaction_hash)
            
            is_a_smart_contract_creation = False
            if transaction_receipt['contractAddress'] is None :
                is_a_smart_contract_creation = True
                log = transaction_receipt["logs"][0]
                print(transaction_receipt)

            
            print('')
    else:
        print('No transactions in block number ' + str(block_number))
        



logger.info("Ethereum node is synced!")


exit()

# Adds all transactions from Ethereum block
def insertion(blockid, tr):
    time = web3.eth.getBlock(blockid)['timestamp']
    for x in range(0, tr):
        trans = web3.eth.getTransactionByBlock(blockid, x)
        # Save also transaction status, should be null if pre byzantium blocks
        status = bool(web3.eth.get_transaction_receipt(trans['hash']).status)
        txhash = trans['hash']
        value = trans['value']
        inputinfo = trans['input']
        # Check if transaction is a contract transfer
        if (value == 0 and not inputinfo.startswith('0xa9059cbb')):
            continue
        fr = trans['from']
        to = trans['to']
        gasprice = trans['gasPrice']
        gas = web3.eth.getTransactionReceipt(trans['hash'])['gasUsed']
        contract_to = ''
        contract_value = ''
        # Check if transaction is a contract transfer
        if inputinfo.startswith('0xa9059cbb'):
            contract_to = inputinfo[10:-64]
            contract_value = inputinfo[74:]
        # Correct contract transfer transaction represents '0x' + 4 bytes 'a9059cbb' + 32 bytes (64 chars) for contract address and 32 bytes for its value
        # Some buggy txs can break up Indexer, so we'll filter it
        if len(contract_to) > 128:
            logger.info('Skipping ' + str(txhash) + ' tx. Incorrect contract_to length: ' + str(len(contract_to)))
            contract_to = ''
            contract_value = ''
        cur.execute(
            'INSERT INTO public.ethtxs(time, txfrom, txto, value, gas, gasprice, block, txhash, contract_to, contract_value, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (time, fr, to, value, gas, gasprice, blockid, txhash, contract_to, contract_value, status))


# Fetch all of new (not in index) Ethereum blocks and add transactions to index
while True:

    maxblockindb = cur.fetchone()[0]
    # On first start, we index transactions from a block number you indicate. 10000000 is a sample.
    if maxblockindb is None:
        maxblockindb = 10000000

    endblock = int(web3.eth.blockNumber)

    logger.info('Current best block in index: ' + str(maxblockindb) + '; in Ethereum chain: ' + str(endblock))

    for block in range(maxblockindb + 1, endblock):
        transactions = web3.eth.getBlockTransactionCount(block)
        if transactions > 0:
            insertion(block, transactions)
        else:
            logger.info('Block ' + str(block) + ' does not contain transactions')

    time.sleep(20)