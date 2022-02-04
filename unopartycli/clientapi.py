import sys
import logging
import binascii
from urllib.parse import quote_plus as urlencode

from unopartylib.lib import config, script
from unopartycli import util
from unopartycli import wallet
from unopartycli import messages
from unopartycli.messages import get_pubkeys

logger = logging.getLogger()

DEFAULT_REQUESTS_TIMEOUT = 5 # seconds

class ConfigurationError(Exception):
    pass

def initialize(testnet=False, testcoin=False, regtest=True, customnet="",
                unoparty_rpc_connect=None, unoparty_rpc_port=None,
                unoparty_rpc_user=None, unoparty_rpc_password=None,
                unoparty_rpc_ssl=False, unoparty_rpc_ssl_verify=False,
                wallet_name=None, wallet_connect=None, wallet_port=None,
                wallet_user=None, wallet_password=None,
                wallet_ssl=False, wallet_ssl_verify=False,
                requests_timeout=DEFAULT_REQUESTS_TIMEOUT):

    def handle_exception(exc_type, exc_value, exc_traceback):
        logger.error("Unhandled Exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.excepthook = handle_exception

    # testnet
    config.TESTNET = testnet or False

    config.REGTEST = regtest or False

    if len(customnet) > 0:
        config.CUSTOMNET = True
        config.REGTEST = True
    else:
        config.CUSTOMNET = False

    # testcoin
    config.TESTCOIN = testcoin or False

    ##############
    # THINGS WE CONNECT TO

    # Server host (Unobtanium Core)
    config.UNOPARTY_RPC_CONNECT = unoparty_rpc_connect or 'localhost'

    # Server RPC port (Unobtanium Core)
    if unoparty_rpc_port:
        config.UNOPARTY_RPC_PORT = unoparty_rpc_port
    else:
        if config.TESTNET:
            config.UNOPARTY_RPC_PORT = config.DEFAULT_RPC_PORT_TESTNET
        elif config.CUSTOMNET:
            config.UNOPARTY_RPC_PORT = config.DEFAULT_RPC_PORT_REGTEST
        elif config.REGTEST:
            config.UNOPARTY_RPC_PORT = config.DEFAULT_RPC_PORT_REGTEST
        else:
            config.UNOPARTY_RPC_PORT = config.DEFAULT_RPC_PORT
    try:
        config.UNOPARTY_RPC_PORT = int(config.UNOPARTY_RPC_PORT)
        if not (int(config.UNOPARTY_RPC_PORT) > 1 and int(config.UNOPARTY_RPC_PORT) <= 65535):
            raise ConfigurationError('invalid RPC port number')
    except:
        raise Exception("Please specific a valid port number unoparty-rpc-port configuration parameter")

    # Server RPC user (Unobtanium Core)
    config.UNOPARTY_RPC_USER = unoparty_rpc_user or 'rpc'

    # Server RPC password (Unobtanium Core)
    if unoparty_rpc_password:
        config.UNOPARTY_RPC_PASSWORD = unoparty_rpc_password
    else:
        config.UNOPARTY_RPC_PASSWORD = None

    # Server RPC SSL
    config.UNOPARTY_RPC_SSL = unoparty_rpc_ssl or False  # Default to off.

    # Server RPC SSL Verify
    config.UNOPARTY_RPC_SSL_VERIFY = unoparty_rpc_ssl_verify or False # Default to off (support self‐signed certificates)

    # Construct server URL.
    config.UNOPARTY_RPC = config.UNOPARTY_RPC_CONNECT + ':' + str(config.UNOPARTY_RPC_PORT)
    if config.UNOPARTY_RPC_PASSWORD:
        config.UNOPARTY_RPC = urlencode(config.UNOPARTY_RPC_USER) + ':' + urlencode(config.UNOPARTY_RPC_PASSWORD) + '@' + config.UNOPARTY_RPC
    if config.UNOPARTY_RPC_SSL:
        config.UNOPARTY_RPC = 'https://' + config.UNOPARTY_RPC
    else:
        config.UNOPARTY_RPC = 'http://' + config.UNOPARTY_RPC
    config.UNOPARTY_RPC += '/rpc/'

    # UNO Wallet name
    config.WALLET_NAME = wallet_name or 'unobtanium'

    # UNO Wallet host
    config.WALLET_CONNECT = wallet_connect or 'localhost'

    # UNO Wallet port
    if wallet_port:
        config.WALLET_PORT = wallet_port
    else:
        if config.TESTNET:
            config.WALLET_PORT = config.DEFAULT_BACKEND_PORT_TESTNET
        elif config.CUSTOMNET:
            config.WALLET_PORT = config.DEFAULT_BACKEND_PORT_REGTEST
        elif config.REGTEST:
            config.WALLET_PORT = config.DEFAULT_BACKEND_PORT_REGTEST
        else:
            config.WALLET_PORT = config.DEFAULT_BACKEND_PORT
    try:
        config.WALLET_PORT = int(config.WALLET_PORT)
        if not (int(config.WALLET_PORT) > 1 and int(config.WALLET_PORT) <= 65535):
            raise ConfigurationError('invalid wallet API port number')
    except:
        raise ConfigurationError("Please specific a valid port number wallet-port configuration parameter")

    # UNO Wallet user
    config.WALLET_USER = wallet_user or 'unobtaniumrpc'

    # UNO Wallet password
    if wallet_password:
        config.WALLET_PASSWORD = wallet_password
    else:
        raise ConfigurationError('wallet RPC password not set. (Use configuration file or --wallet-password=PASSWORD)')

    # UNO Wallet SSL
    config.WALLET_SSL = wallet_ssl or False  # Default to off.

    # UNO Wallet SSL Verify
    config.WALLET_SSL_VERIFY = wallet_ssl_verify or False # Default to off (support self‐signed certificates)

    # Construct UNO wallet URL.
    config.WALLET_URL = urlencode(config.WALLET_USER) + ':' + urlencode(config.WALLET_PASSWORD) + '@' + config.WALLET_CONNECT + ':' + str(config.WALLET_PORT)
    if config.WALLET_SSL:
        config.WALLET_URL = 'https://' + config.WALLET_URL
    else:
        config.WALLET_URL = 'http://' + config.WALLET_URL

    config.REQUESTS_TIMEOUT = requests_timeout

    # Encoding
    if config.TESTCOIN:
        config.PREFIX = b'XX'                   # 2 bytes (possibly accidentally created)
    else:
        config.PREFIX = b'CNTRPRTY'             # 8 bytes

    # (more) Testnet
    if config.TESTNET:
        config.MAGIC_BYTES = config.MAGIC_BYTES_TESTNET
        if config.TESTCOIN:
            config.ADDRESSVERSION = config.ADDRESSVERSION_TESTNET
            config.P2SH_ADDRESSVERSION = config.P2SH_ADDRESSVERSION_TESTNET
            config.BLOCK_FIRST = config.BLOCK_FIRST_TESTNET_TESTCOIN
            config.BURN_START = config.BURN_START_TESTNET_TESTCOIN
            config.BURN_END = config.BURN_END_TESTNET_TESTCOIN
            config.UNSPENDABLE = config.UNSPENDABLE_TESTNET
            config.UNSPENDSTORAGE = config.UNSPENDSTORAGE_TESTNET
        else:
            config.ADDRESSVERSION = config.ADDRESSVERSION_TESTNET
            config.P2SH_ADDRESSVERSION = config.P2SH_ADDRESSVERSION_TESTNET
            config.BLOCK_FIRST = config.BLOCK_FIRST_TESTNET
            config.BURN_START = config.BURN_START_TESTNET
            config.BURN_END = config.BURN_END_TESTNET
            config.UNSPENDABLE = config.UNSPENDABLE_TESTNET
            config.UNSPENDSTORAGE = config.UNSPENDSTORAGE_TESTNET
    elif config.CUSTOMNET:
        custom_args = customnet.split('|')

        if len(custom_args) == 3:
            config.MAGIC_BYTES = config.MAGIC_BYTES_REGTEST
            config.ADDRESSVERSION = binascii.unhexlify(custom_args[1])
            config.P2SH_ADDRESSVERSION = binascii.unhexlify(custom_args[2])
            config.BLOCK_FIRST = config.BLOCK_FIRST_REGTEST
            config.BURN_START = config.BURN_START_REGTEST
            config.BURN_END = config.BURN_END_REGTEST
            config.UNSPENDABLE = custom_args[0]
        else:
            raise "Custom net parameter needs to be like UNSPENDABLE_ADDRESS|ADDRESSVERSION|P2SH_ADDRESSVERSION (version bytes in HH format)"
    elif config.REGTEST:
        config.MAGIC_BYTES = config.MAGIC_BYTES_REGTEST
        if config.TESTCOIN:
            config.ADDRESSVERSION = config.ADDRESSVERSION_REGTEST
            config.P2SH_ADDRESSVERSION = config.P2SH_ADDRESSVERSION_REGTEST
            config.BLOCK_FIRST = config.BLOCK_FIRST_REGTEST_TESTCOIN
            config.BURN_START = config.BURN_START_REGTEST_TESTCOIN
            config.BURN_END = config.BURN_END_REGTEST_TESTCOIN
            config.UNSPENDABLE = config.UNSPENDABLE_REGTEST
            config.UNSPENDSTORAGE = config.UNSPENDSTORAGE_REGTEST
        else:
            config.ADDRESSVERSION = config.ADDRESSVERSION_REGTEST
            config.P2SH_ADDRESSVERSION = config.P2SH_ADDRESSVERSION_REGTEST
            config.BLOCK_FIRST = config.BLOCK_FIRST_REGTEST
            config.BURN_START = config.BURN_START_REGTEST
            config.BURN_END = config.BURN_END_REGTEST
            config.UNSPENDABLE = config.UNSPENDABLE_REGTEST
            config.UNSPENDSTORAGE = config.UNSPENDSTORAGE_REGTEST
    else:
        config.MAGIC_BYTES = config.MAGIC_BYTES_MAINNET
        if config.TESTCOIN:
            config.ADDRESSVERSION = config.ADDRESSVERSION_MAINNET
            config.P2SH_ADDRESSVERSION = config.P2SH_ADDRESSVERSION_MAINNET
            config.BLOCK_FIRST = config.BLOCK_FIRST_MAINNET_TESTCOIN
            config.BURN_START = config.BURN_START_MAINNET_TESTCOIN
            config.BURN_END = config.BURN_END_MAINNET_TESTCOIN
            config.UNSPENDABLE = config.UNSPENDABLE_MAINNET
            config.UNSPENDSTORAGE = config.UNSPENDSTORAGE_MAINNET
        else:
            config.ADDRESSVERSION = config.ADDRESSVERSION_MAINNET
            config.P2SH_ADDRESSVERSION = config.P2SH_ADDRESSVERSION_MAINNET
            config.BLOCK_FIRST = config.BLOCK_FIRST_MAINNET
            config.BURN_START = config.BURN_START_MAINNET
            config.BURN_END = config.BURN_END_MAINNET
            config.UNSPENDABLE = config.UNSPENDABLE_MAINNET
            config.UNSPENDSTORAGE = config.UNSPENDSTORAGE_MAINNET

WALLET_METHODS = [
    'get_wallet_addresses', 'get_btc_balances', 'sign_raw_transaction',
    'get_pubkey', 'is_valid', 'is_mine', 'get_btc_balance', 'send_raw_transaction',
    'wallet', 'asset', 'balances', 'pending', 'is_locked', 'unlock', 'wallet_last_block',
    'sweep'
]

def call(method, args, pubkey_resolver=None):
    """
        Unified function to call Wallet and Server API methods
        Should be used by applications like `unoparty-gui`

        :Example:

        import unopartycli.clientapi
        clientapi.initialize(...)
        unsigned_hex = clientapi.call('create_send', {...})
        signed_hex =  clientapi.call('sign_raw_transaction', unsigned_hex)
        tx_hash = clientapi.call('send_raw_transaction', signed_hex)
    """
    if method in WALLET_METHODS:
        func = getattr(wallet, method)
        return func(**args)
    else:
        if method.startswith('create_'):
            # Get provided pubkeys from params.
            pubkeys = []
            for address_name in ['source', 'destination']:
                if address_name in args:
                    address = args[address_name]
                    if script.is_multisig(address) or address_name != 'destination':    # We don’t need the pubkey for a mono‐sig destination.
                        pubkeys += get_pubkeys(address, pubkey_resolver=pubkey_resolver)
            args['pubkey'] = pubkeys

        result = util.api(method, args)

        if method.startswith('create_'):
            messages.check_transaction(method, args, result)

        return result


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
