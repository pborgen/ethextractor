import argparse
from logger import Logger
from hex.hex_contract_extract import HexContractExtract

def hex_getall(args):
    hexContractExtract = HexContractExtract()
    hexContractExtract.extract_contract_data()

    print('Hello, {0}!'.format(args.name))


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

hex_parser = subparsers.add_parser('hex')
hex_parser.add_argument('getall')  # add the name argument
hex_parser.set_defaults(func=hex_getall)  # set the default function to hello

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)  # call the default function