from web3 import Web3
from web3.auto import w3
import json
import logging
import sys
from pathlib import Path
from ethextractor.environment.properties import Properties
from ethextractor.helper.byte_helper import ByteHelper
import pandas as pd 
import csv
import concurrent.futures


class HexContractExtract:

    hexContractAddress = '0x2b591e99afe9f32eaa6214f7b7629768c40eeb39'
    hex_origion_block_number = 9041184
    hex_first_block_with_a_transaction = 9041244
    web3 = None
    abi_json = None
    contract = None


    def __init__(self):
        web3url = Properties().getWeb3Providerurl()

        self.web3 = Web3(Web3.HTTPProvider(web3url))
        self.abi_json = self.getHexABI()
        self.byteHelper = ByteHelper()

        self.contract = w3.eth.contract(address=Web3.toChecksumAddress(self.hexContractAddress), abi=self.abi_json)

    def iterate_blocks_find_hex_contract_transactions_concurrent(self):

        transactions_list = []
        processed_blocks_list = []
        future_result_list = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            # Start the load operations and mark each future with its URL
            for block_number in range(self.hex_first_block_with_a_transaction, self.hex_first_block_with_a_transaction + 1000000):
                future_result_list = {
                    executor.submit(self.process_block_get_transactions_with_hex_contract, block_number)
                }
                processed_blocks_list.append(block_number)
            
            
            for future in concurrent.futures.as_completed(future_result_list):
                #transaction_hash = future_result_list[future]
                try:
                    result_list = future.result()
                    if len(result_list) > 0:
                        transactions_list.extend(result_list)
                    
                except Exception as exc:
                    print(' generated an exception: ' + exc)
                else:
                    print(' here' )

    
        df = pd.DataFrame(data={"block_number": processed_blocks_list})
        df.to_csv("C:/ETHEXTRACTOR/blocks_processes.csv", sep=',',index=False)

        # with open('C:/ETHEXTRACTOR/blocks_processes.csv','w') as result_file:
        #     wr = csv.writer(result_file, dialect='excel')
        #     wr.writerows(processed_blocks_list)

        
        # with open('C:/ETHEXTRACTOR/transactions_with_hex_contract.csv','w') as result_file:
        #     wr = csv.writer(result_file, dialect='excel')
        #     wr.writerows(transactions_list)
        df = pd.DataFrame(data={"transaction_hash": transactions_list})
        df.to_csv("C:/ETHEXTRACTOR/hex_transactions.csv", sep=',',index=False)

    def iterate_blocks_find_hex_contract_transactions(self):
        #current_block_number = self.web3.eth.get_block('latest').number
        
        transactions_list = []
        processed_blocks_list = []

        for block_number in range(self.hex_first_block_with_a_transaction, self.hex_origion_block_number + 1000):

            transactions_list.extend(self.process_block_get_transactions_with_hex_contract(block_number))

            processed_blocks_list.append(block_number) 

        with open('C:/ETHEXTRACTOR/blocks_processes.csv','w') as result_file:
            wr = csv.writer(result_file, dialect='excel')
            wr.writerows(processed_blocks_list)

        
        with open('C:/ETHEXTRACTOR/transactions_with_hex_contract.csv','w') as result_file:
            wr = csv.writer(result_file, dialect='excel')
            wr.writerows(transactions_list)

    def iterate_blocks_extract_all_info(self):
        #current_block_number = self.web3.eth.get_block('latest').number
        
        transactions_list = []
        processed_blocks_list = []

        for block_number in range(self.hex_origion_block_number, self.hex_origion_block_number + 100000):

            transactions_list.extend(self.process_block(block_number))

            processed_blocks_list.append(block_number)
            #print("Processed Blocknumber: " + str(block_number))    

        pass
            # transaction_count = self.web3.eth.get_block_transaction_count(block_number)
            # if transaction_count > 0:
            #     for x in range(0, transaction_count):
            #         transaction = self.web3.eth.get_transaction_by_block(block_number, x)
            #         transaction_hash = transaction['hash']
            #         transaction_transactionIndex = transaction['transactionIndex']
            #         transaction_blockHash = transaction['blockHash']
            #         transaction_blocknumber = transaction['blockNumber']
            #         transaction_value = transaction['value']
            #         transaction_input = transaction['input']
            #         transaction_from = transaction['from']
            #         transaction_to = transaction['to']
            #         transaction_gasprice = transaction['gasPrice']
            #         #transaction_maxFeePerGas = transaction['maxFeePerGas']
            #         #transaction_maxPriortyFeePerGas = transaction['maxPriortyFeePerGas']
            #         transaction_gas = transaction['gas']

            #         transaction_receipt = self.web3.eth.get_transaction_receipt(transaction_hash)
                    
            #         is_a_smart_contract_creation = False
            #         if transaction_receipt['contractAddress'] is None :
            #             is_a_smart_contract_creation = True
            #             log = transaction_receipt["logs"][0]
            #             print(transaction_receipt)

                    
            #         print('')
            # else:
            #     print('No transactions in block number ' + str(block_number))

    def process_block_get_transactions_with_hex_contract(self, block_number: int) -> list:
        block = self.web3.eth.get_block(block_number)
        transactions = block.transactions

        transactions_with_hex_contract_list = []

        for element in transactions:
            transaction_hash_string = element.hex()

            is_transaction_with_hex_contract = self.is_transaction_with_hex_contract(transaction_hash_string)

            if is_transaction_with_hex_contract:
                transactions_with_hex_contract_list.append(transaction_hash_string)

        print("Processed Blocknumber: " + str(block_number))

        return transactions_with_hex_contract_list

    def process_block(self, block_number: int) -> list:
        block = self.web3.eth.get_block(block_number)
        transactions = block.transactions

        transactions_list = []

        for element in transactions:
            transaction_hash_string = element.hex()

            hashMap = self.extract_data_fromTransaction(transaction_hash_string)

            if hashMap is not None:
                transactions_list.append(hashMap)

        print("Processed Blocknumber: " + str(block_number))

        return transactions_list

    def is_transaction_with_hex_contract(self, transaction_hash):
        transaction = self.web3.eth.get_transaction(transaction_hash)

        if transaction['to'] is not None and transaction['to'].lower() == self.hexContractAddress:
            return True
        else:
            return False

    def extract_data_fromTransaction(self, transaction_hash: str):
        
        transaction = self.web3.eth.get_transaction(transaction_hash)
        returnData = None

        # Check if this transaction is with the hex contract
        if transaction['to'] is not None and transaction['to'].lower() == self.hexContractAddress:
            returnData = {}

            func_obj, func_params = self.contract.decode_function_input(transaction["input"])     

            contract_method_name = func_obj.function_identifier
            returnData['contract_method_name'] = contract_method_name
            returnData['block_number'] = transaction.blockNumber
            returnData['nonce'] = transaction.nonce
            returnData['transaction_hash'] = transaction_hash

            # Retrieve the input parameters
            if contract_method_name == 'stakeStart':
                returnData['newStakedHearts'] = func_params['newStakedHearts']
                returnData['newStakedDays'] = func_params['newStakedDays']
                
            elif contract_method_name == 'stakeEnd':
                returnData['stakeIndex'] = func_params['stakeIndex']
                returnData['stakeIdParam'] = func_params['stakeIdParam']
                
            else:
                logging.warn('We are not processing the folowing method name = ' + contract_method_name)


            returnData = self.retrieveDataFromReceipt(transaction_hash, returnData)

            logging.info('Processed Transaction=' + transaction_hash)

        return returnData


    # Retrieve the data from the emitted logs aka receipt
    # in the future this can be done in parallel
    def retrieveDataFromReceipt(self, transaction_hash: str, returnData):
        receipt = self.web3.eth.get_transaction_receipt(transaction_hash)
        contract_method_name = returnData['contract_method_name']
        event_name = None
        decoded_logs = None
        processLog = None

        if contract_method_name == 'stakeStart':
            event_name = 'StakeStart'
            decoded_logs = self.contract.events[event_name]().processReceipt(receipt)[0]
            args = decoded_logs.args
            returnData['stakeId'] = args.stakeId
            returnData['data0'] = args.data0

            # convert data0
            my_bytes = self.byteHelper.int_to_bytes(args.data0)
            len_bytes = len(my_bytes)

            # we start at the end of the bytes and walk backwards
            read_bytes_end = len_bytes # 24
            read_bytes_start = len_bytes - 5 # 19
            timestamp_bytes = my_bytes[read_bytes_start : read_bytes_end]
            timestamp_int = self.byteHelper.bytes_to_int(timestamp_bytes)
            
            read_bytes_end = read_bytes_start # 19 
            read_bytes_start = read_bytes_start - 9 # 10
            stakedHearts_bytes = my_bytes[read_bytes_start : read_bytes_end]
            stakedHearts_int = self.byteHelper.bytes_to_int(stakedHearts_bytes)

            read_bytes_end = read_bytes_start # 10 
            read_bytes_start = read_bytes_start - 9 # 1
            stakeShares_bytes = my_bytes[read_bytes_start : read_bytes_end]
            stakeShares_int = self.byteHelper.bytes_to_int(stakeShares_bytes)

            read_bytes_end = read_bytes_start # 1
            read_bytes_start = read_bytes_start - 1 # 0
            stakedDays_bytes = my_bytes[read_bytes_start : read_bytes_end]
            stakedDays_int = self.byteHelper.bytes_to_int(stakedDays_bytes)
        
            returnData['timestamp'] = timestamp_int
            returnData['stakedHearts'] = stakedHearts_int
            returnData['stakeShares'] = stakeShares_int
            returnData['stakedDays'] = stakedDays_int
            #returnData['isAutoStake'] = 0

            #processLog = self.contract.events[event_name]().processLog(receipt['logs'][0])
        elif contract_method_name == 'stakeEnd':
            event_name = 'StakeEnd'
            decoded_logs = self.contract.events[event_name]().processReceipt(receipt)[0]
            args = decoded_logs.args
            returnData['data0'] = args.data0
            returnData['data1'] = args.data1

            # convert data0
            my_bytes = self.byteHelper.int_to_bytes(args.data0)
            len_bytes = len(my_bytes)

            # we start at the end of the bytes and walk backwards
            read_bytes_end = len_bytes 
            read_bytes_start = len_bytes - 5 
            timestamp_bytes = my_bytes[read_bytes_start : read_bytes_end]
            timestamp_int = self.byteHelper.bytes_to_int(timestamp_bytes)
            returnData['timestamp'] = timestamp_int

            read_bytes_end = read_bytes_start 
            read_bytes_start = read_bytes_start - 9 
            stakedHearts_bytes = my_bytes[read_bytes_start : read_bytes_end]
            stakedHearts_int = self.byteHelper.bytes_to_int(stakedHearts_bytes)
            returnData['stakedHearts'] = stakedHearts_int

            read_bytes_end = read_bytes_start 
            read_bytes_start = read_bytes_start - 9
            if read_bytes_start >= 0:
                stakeShares_bytes = my_bytes[read_bytes_start : read_bytes_end]
                stakeShares_int = self.byteHelper.bytes_to_int(stakeShares_bytes)
                returnData['stakeShares'] = stakeShares_int
            else:
                returnData['stakeShares'] = -1

            read_bytes_end = read_bytes_start 
            read_bytes_start = read_bytes_start - 9
            if read_bytes_start >= 0:
                payout_bytes = my_bytes[read_bytes_start : read_bytes_end]
                payout_int = self.byteHelper.bytes_to_int(payout_bytes)
                returnData['payout'] = payout_int
            else:
                returnData['payout'] = -1

            # convert data1
            my_bytes = self.byteHelper.int_to_bytes(args.data1)
            len_bytes = len(my_bytes)

             # we start at the end of the bytes and walk backwards
            read_bytes_end = len_bytes 
            read_bytes_start = len_bytes - 9
            penalty_bytes = my_bytes[read_bytes_start : read_bytes_end]
            penalty_int = self.byteHelper.bytes_to_int(penalty_bytes)
            returnData['penalty'] = penalty_int

            read_bytes_end = read_bytes_start 
            read_bytes_start = read_bytes_start - 2
            if read_bytes_start >= 0:
                servedDays_bytes = my_bytes[read_bytes_start : read_bytes_end]
                servedDays_int = self.byteHelper.bytes_to_int(servedDays_bytes)
                returnData['servedDays'] = servedDays_int
            else:
                returnData['servedDays'] = -1
            
        else:
            logging.warn('We are not processing the folowing method name = ' + contract_method_name)
        print(returnData)
        return returnData


    def __parseData0(self, data0, returnData):
        data0_bytes = self.byteHelper.int_to_bytes(data0)

        # timestamp
        timestamp_bytes = data0_bytes[19:24]
        timestamp_int = self.byteHelper.bytes_to_int(timestamp_bytes)
        returnData['timestamp'] = timestamp_int

        print('done')

    def getHexABI(self):
        abi_json = None

        p = Path(__file__).with_name('hex_abi.json')
        with p.open('r') as f:
            abi_json = json.load(f)
        
        return abi_json