import os
from prettytable import PrettyTable
from unopartycli import wallet, util
from unopartylib.lib import config

# TODO: inelegant
def get_view(view_name, args):
    if view_name == 'balances':
        return wallet.balances(args.address)
    elif view_name == 'asset':
        return wallet.asset(args.asset)
    elif view_name == 'wallet':
        return wallet.wallet()
    elif view_name == 'pending':
        return wallet.pending()
    elif view_name == 'getinfo':
        return util.api('get_running_info')
    elif view_name == 'get_tx_info':
        return util.api('get_tx_info', {'tx_hex': args.tx_hex})
    elif view_name == 'getrows':
        method = 'get_{}'.format(args.table)
        if args.filter:
            filters = [tuple(f) for f in args.filter]
        else:
            filters = []
        params = {
            'filters': filters,
            'filterop': args.filter_op,
            'order_by': args.order_by,
            'order_dir': args.order_dir,
            'start_block': args.start_block,
            'end_block': args.end_block,
            'status': args.status,
            'limit': args.limit,
            'offset': args.offset
        }
        return util.api(method, params)

def print_balances(balances):
    lines = []
    lines.append('')
    lines.append('Address Balances')
    table = PrettyTable(['Asset', 'Amount'])
    for asset in balances:
        table.add_row([asset, balances[asset]])
    lines.append(table.get_string())
    lines.append('')
    print(os.linesep.join(lines))

def print_asset(asset):
    if asset['asset'] == config.XCP or asset['asset'] == config.BTC:
        meltable = False
        backvalue = 0
        backing_asset = 'None'
    else:
        backvalue = asset['backing']
        backing_asset = asset['backing_asset']
        meltable = asset['meltable']
        if util.is_divisible(asset['backing_asset']) and bool(asset['meltable']):
            backvalue = asset['backing']/100000000

    lines = []
    lines.append('')
    lines.append('Asset Details')
    table = PrettyTable(header=False, align='l')
    table.add_row(['Asset Name:', asset['asset']])
    table.add_row(['Asset ID:', asset['asset_id']])
    table.add_row(['Divisible:', asset['divisible']])
    table.add_row(['Meltable:', meltable])
    if meltable:
        table.add_row(['Backing Asset:', backing_asset])
        table.add_row(['Backing per Asset:', backvalue])
    table.add_row(['Locked:', asset['locked']])
    table.add_row(['Supply:', asset['supply']])
    table.add_row(['Issuer:', asset['issuer']])
    table.add_row(['Description:', '‘' + asset['description'] + '’'])
    table.add_row(['Balance:', asset['balance']])
    lines.append(table.get_string())

    if asset['addresses']:
        lines.append('')
        lines.append('Wallet Balances')
        table = PrettyTable(['Address', 'Balance'])
        for address in asset['addresses']:
            balance = asset['addresses'][address]
            table.add_row([address, balance])
        lines.append(table.get_string())

    if asset['asset'] != config.BTC:
        if asset['sends']:
            lines.append('')
            lines.append('Wallet Sends and Receives')
            table = PrettyTable(['Type', 'Quantity', 'Source', 'Destination'])
            i = 0
            for send in asset['sends']:
                if not ((send['source'] == config.UNSPENDSTORAGE) or (send['destination'] == config.UNSPENDSTORAGE)):
                    i = i + 1
                    table.add_row([send['type'], send['quantity'], send['source'], send['destination']])
            if i == 0:
                lines.append('none')
                lines.append('')
            lines.append('Assets Stored and Melts')
            for send in asset['sends']:
                if send['source'] == config.UNSPENDSTORAGE:
                    table.add_row(['redeemed', send['quantity'], send['source'], send['destination']])
                if send['destination'] == config.UNSPENDSTORAGE:
                    table.add_row(['stored', send['quantity'], send['source'], send['destination']])
            lines.append(table.get_string())

    lines.append('')
    print(os.linesep.join(lines))

def print_wallet(wallet):
    lines = []
    for address in wallet['addresses']:
        table = PrettyTable(['Asset', 'Balance'])
        for asset in wallet['addresses'][address]:
            balance = wallet['addresses'][address][asset]
            table.add_row([asset, balance])
        lines.append(address)
        lines.append(table.get_string())
        lines.append('')
    total_table = PrettyTable(['Asset', 'Balance'])
    for asset in wallet['assets']:
        balance = wallet['assets'][asset]
        total_table.add_row([asset, balance])
    lines.append('TOTAL')
    lines.append(total_table.get_string())
    lines.append('')
    print(os.linesep.join(lines))

def print_pending(awaiting_btcs):
    table = PrettyTable(['Matched Order ID', 'Time Left'])
    for order_match in awaiting_btcs:
        order_match = format_order_match(order_match)
        table.add_row(order_match)
    print(table)

def print_getrows(rows):
    if len(rows) > 0:
        headers = list(rows[0].keys())
        table = PrettyTable(headers)
        for row in rows:
            values = list(row.values())
            table.add_row(values)
        print(table)
    else:
        print("No result.")

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
