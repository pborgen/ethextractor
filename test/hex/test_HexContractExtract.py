import unittest
import sys
from ethextractor.helper.byte_helper import ByteHelper
from ethextractor.hex.hex_contract_extract import HexContractExtract
from ethextractor.helper.byte_helper import ByteHelper

class TestHexContractExtract(unittest.TestCase):
    hex_stake_start_transaction_hash = '0x01cf40fc2c635f08da718af8b649a59f183bfe45399fb5b4e15b5c22b9b62b59'
    hex_stake_end_transaction_hash = '0x352ae111f775fcd657cfde56ba79123da9ea69fc6e2ac16efd3e7ccfb9951da6'

    def setUp(self):
        self.hexContractExtract = HexContractExtract()

    # def test_extract_start_stake_info(self):
    #     obj = \
    #         self.hexContractExtract.extract_data_fromTransaction(self.hex_stake_start_transaction_hash)
        
    #     self.assertIsNotNone(obj)
    
    # def test_extract_end_stake_info(self):
    #     obj = \
    #         self.hexContractExtract.extract_data_fromTransaction(self.hex_stake_end_transaction_hash)
        
    #     self.assertIsNotNone(obj)

    # def test_iterate_blocks(self):
    #     obj = \
    #         self.hexContractExtract.iterate_blocks()
        
    #     self.assertIsNotNone(obj)

    def test_gather_all_transactions_with_hex_contract(self):
        obj = \
            self.hexContractExtract.iterate_blocks_find_hex_contract_transactions_concurrent()
        
        self.assertIsNotNone(obj)

    # def test_process_block(self):
    #     obj = \
    #         self.hexContractExtract.process_block(13399301)
        
    #     self.assertIsNotNone(obj)

    # def test_parse(self):
    #     bla = 1618315291154829038232450090540942832493609856928446947781

    #     byteHelper = ByteHelper()
    #     my_bytes = byteHelper.int_to_bytes(bla)
        
    #     len_bytes = len(my_bytes)
        
    #     timestamp_bytes = my_bytes[19:24]
    #     stakedHearts_bytes = my_bytes[10:19]
    #     stakeShares_bytes = my_bytes[1:10]
    #     stakedDays_bytes = my_bytes[0:1]

        
    #     timestamp_int = byteHelper.bytes_to_int(timestamp_bytes)
    #     stakedHearts_int = byteHelper.bytes_to_int(stakedHearts_bytes)
    #     stakeShares_int = byteHelper.bytes_to_int(stakeShares_bytes)
    #     stakedDays_int = byteHelper.bytes_to_int(stakedDays_bytes)
        
        

    #     my_int = byteHelper.bytes_to_int(my_bytes)

    #     print('done')



       

if __name__ == '__main__':
    unittest.main()
