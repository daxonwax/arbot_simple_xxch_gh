
################################################
################################################

"""
CAUTION: quantities (eg top_bid_qty_BTC) may have to be in string format, not float
"""


# import inspect

import time as TM
# from itertools import product
# from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing.dummy
# import shrimpy
# from sorcery import dict_of
from tabulate import tabulate
# import common_exchange_pairs


import os

import credentials
import fee_schedule
import k_decoratorKit
import k_shrimpyKit
import k_toolKit


PUBLIC_KEY = credentials.passport["shrimpy"]["API_KEY"]
PRIVATE_KEY = credentials.passport["shrimpy"]["API_SECRET"]

TK = k_toolKit.Toolkit()
SK = k_shrimpyKit.Shrimpykit(PUBLIC_KEY, PRIVATE_KEY)
DK = k_decoratorKit.Decoratorkit()
MASTER_TIMESTAMP = TK.create_timestamp(forfile=True)

# EXCHANGE_PAIRS = common_exchange_pairs.exchange_pairs
THRESHOLD = 0.50
PRO_RATA_MULTIPLIER = 0.01
MAXPROFIT_USD = -10000000000
ADJ_MAXPROFIT_USD = -10000000000
EXCHANGES = ("binance", "hitbtc", "kucoin")
# GOODLIST = ["PAX", "USDT", "USDC", "TUSD", "USD"]
GOODLIST = ["USDT", "USD"]
BASE_CURRENCY = "BTC"

CSV_FILE_PATH_PLACED = f"csv/placed/csv_file{MASTER_TIMESTAMP}.csv"
CSV_FILE_PATH_NONE =  f"csv/none/csv_file{MASTER_TIMESTAMP}.csv"

SPACE = TK.spacer
LINE = TK.liner
# seperator = u"\u2015"*42
_ = "                        _"
top_bid_prc_BTC = 0.01
pro_rata_bid_BTC = 0.01
# "sell_on" : f"sell on {top_bid_xch:<9} for {float(top_bid - bid_fee):<.7f}",
# "buy_on" : f"buy on {top_ask_xch:<10} for {float(top_ask - ask_fee):<.7f}",


# get_account_balances took 2080745.254 microseconds

# @DK.print_timing
def get_account_balances(SK,
                         TK,
                         approved_list_of_syms,
                         storage_dictionary={},
                         ):

    for xch in credentials.passport["shrimpy"]["ACCOUNTS"]:

        storage_dictionary[xch] = {}

        balance = SK.client.get_balance(
            credentials.passport["shrimpy"]["USER_ID"],
            credentials.passport["shrimpy"]["ACCOUNTS"][xch]["ID"],
        )

        for entry in balance["balances"]:
            sym = entry["symbol"]
            if sym in approved_list_of_syms:
                nativeValue = entry["nativeValue"]
                btcValue = entry["btcValue"]
                usdValue = entry["usdValue"]
                storage_dictionary[xch]["symbol"] = sym
                storage_dictionary[xch]["nativeValue"] = nativeValue
                storage_dictionary[xch]["btcValue"] = btcValue
                storage_dictionary[xch]["usdValue"] = usdValue

    return storage_dictionary


# @DK.print_timing
def sanitize_data(toolkit, orderbooks, goodlist):

    orderbooks_N = toolkit.create_named_dict_from_key(
        orderbooks, "quoteSymbol", goodlist)
    orderbooks_N["USDT"]["orderBooks"] += orderbooks_N["USD"]["orderBooks"]
    del orderbooks_N["USD"]
    return orderbooks_N


# @DK.print_timing
def organize_data(sym_data):
    base_syms, quote_syms, xchs, bid_prcs, bid_qtys, ask_prcs, ask_qtys = zip(
        *[
            [
                sym_data["baseSymbol"],
                sym_data["quoteSymbol"],
                xch_data["exchange"],
                xch_data["orderBook"]["bids"][0]["price"],
                xch_data["orderBook"]["bids"][0]["quantity"],
                xch_data["orderBook"]["asks"][0]["price"],
                xch_data["orderBook"]["asks"][0]["quantity"]
            ]
            for xch_data in sym_data[
                "orderBooks"
            ]  # if quote_asset in ["PAX", "USDT", "USDC", "TUSD"]
        ]
    )
    return base_syms, quote_syms, xchs, bid_prcs, bid_qtys, ask_prcs, ask_qtys

# @DK.print_timing


def find_top_bid_ask(
        base_syms, quote_syms, xchs,  bid_prcs, bid_qtys, ask_prcs, ask_qtys):

    base_sym = base_syms[0]
    quote_sym = quote_syms[0]

    top_bid_idx = bid_prcs.index(max(bid_prcs))
    top_bid_xch = xchs[top_bid_idx]
    top_bid_prc_USD = float(bid_prcs[top_bid_idx])
    top_bid_qty_BTC = float(bid_qtys[top_bid_idx])

    top_ask_idx = ask_prcs.index(min(ask_prcs))
    top_ask_xch = xchs[top_ask_idx]
    top_ask_prc_USD = float(ask_prcs[top_ask_idx])
    top_ask_qty_BTC = float(ask_qtys[top_ask_idx])

    return (
        base_sym,
        quote_sym,
        top_bid_xch,
        top_bid_prc_USD,
        top_bid_qty_BTC,
        top_ask_xch,
        top_ask_prc_USD,
        top_ask_qty_BTC
    )

# @DK.print_timing
def map_top_xch_to_balance(balance_values, top_bid_xch, top_ask_xch):
    bid_acct_bal_BTC = balance_values[top_bid_xch.lower()]["btcValue"]
    bid_acct_bal_USD = balance_values[top_bid_xch.lower()]["usdValue"]
    ask_acct_bal_BTC = balance_values[top_ask_xch.lower()]["btcValue"]
    ask_acct_bal_USD = balance_values[top_ask_xch.lower()]["usdValue"]

    return bid_acct_bal_BTC, bid_acct_bal_USD, ask_acct_bal_BTC, ask_acct_bal_USD


# @DK.print_timing
def calculate_fees(xch,  fee_class="trading"):
    return fee_schedule.fees[xch.lower()][fee_class]


# @DK.print_timing
def calculate_profit(
        top_bid_prc,  top_ask_prc, top_bid_fee, top_ask_fee):

    bid_inc_fees = top_bid_prc * (1 - top_bid_fee)
    ask_inc_fees = top_ask_prc / (1 - top_ask_fee)
    profit_inc_fees = bid_inc_fees - ask_inc_fees

    return bid_inc_fees, ask_inc_fees, profit_inc_fees


# @DK.print_timing
def update_maxprofit(profit, maxprofit):
    return max(profit, maxprofit)

# @DK.print_timing


def pro_rate(val, rate_amt=PRO_RATA_MULTIPLIER):
    return val*rate_amt

# @DK.print_timing


def update_profit(profit_list):
    return [pro_rate(val) for val in profit_list]

# @DK.print_timing


def display_run(
            toolkit,
            now,
            run,
            base_sym,
            quote_sym,
            top_bid_xch,
            top_ask_xch,
            bid_acct_bal_BTC,
            bid_acct_bal_USD,
            ask_acct_bal_BTC,
            ask_acct_bal_USD,
            top_bid_prc_USD,
            top_ask_prc_USD,
            top_bid_fee_USD,
            top_ask_fee_USD,
            bid_inc_fees_USD,
            ask_inc_fees_USD,
            profit_inc_fees_USD,
            pro_rated_bid_inc_fees_USD,
            pro_rated_ask_inc_fees_USD,
            pro_rated_profit_inc_fees_USD,
            TTL_BALANCE_BTC,
            TTL_BALANCE_USD,
            proceed=False,
            description=None,


            ):
    SPACE(vertical=1)
    toolkit.cprint_inspect(now, fg_color="lightOrange")
    toolkit.cprint_inspect(run, fg_color="lightOrange")

    SPACE(vertical=1)
    toolkit.multiprint([base_sym, quote_sym])
    SPACE(vertical=1)
    LINE()

    SPACE(vertical=1)
    # toolkit.multiprint([top_bid_prc_USD, top_bid_fee_USD])
    toolkit.cprint_inspect(top_bid_prc_USD, fg_color="lightGray")
    toolkit.cprint_inspect(top_bid_fee_USD, fg_color="gray")
    toolkit.cprint_inspect(bid_inc_fees_USD, fg_color="gray")
    toolkit.cprint_inspect(pro_rated_bid_inc_fees_USD, fg_color="seaGreen")
    # toolkit.multiprint([pro_rated_bid_inc_fees_USD])
    SPACE(vertical=1)
    # toolkit.multiprint([top_ask_prc_USD, top_ask_fee_USD])
    toolkit.cprint_inspect(top_ask_prc_USD, fg_color="lightGray")
    toolkit.cprint_inspect(top_ask_fee_USD, fg_color="gray")
    toolkit.cprint_inspect(ask_inc_fees_USD, fg_color="gray")
    toolkit.cprint_inspect(pro_rated_ask_inc_fees_USD, fg_color="lightOrange")
    # toolkit.multiprint([pro_rated_ask_inc_fees_USD])
    SPACE(vertical=1)
    SPACE(vertical=1)
    toolkit.cprint_inspect(
    pro_rated_profit_inc_fees_USD,
    fg_color=toolkit.create_truthy_index(
        pro_rated_profit_inc_fees_USD)["fg_color"],
    bg_color=toolkit.create_truthy_index(pro_rated_profit_inc_fees_USD)["bg_color"])

    if proceed:
        SPACE(vertical=1)
        LINE()
        LINE()
        SPACE(vertical=1)
        toolkit.cprint(
             "            ARBITRAGE OPPORTUNITY          ",
            fg_color="ghostWhite",
            bg_color="green"
                        )
    
        SPACE(vertical=1)
        LINE()
        SPACE(vertical=1)
        toolkit.multiprint([bid_acct_bal_BTC, ask_acct_bal_USD])

        SPACE(vertical=1)

        LINE()
        SPACE(vertical=1)
        print(
            f"   @{top_bid_xch:<8}: {float(0.01):>7.03f} BTC   >>>    {float(pro_rated_bid_inc_fees_USD):>7.03f} USDT")
        # print(f"Buy 1 BTC on {top_ask_xch} for {top_ask_prc_USD }")
        # print(f"Sell {float(top_ask_prc_USD):>7.03f }USDT on {top_ask_xch:<11} for 1BTC      ")
        print(
            f"   @{top_ask_xch:<8}: {float(pro_rated_ask_inc_fees_USD):>7.03f} USDT  >>>    {float(0.01):>7.03f} BTC")
        SPACE(vertical=1)
        LINE()
        SPACE(vertical=1)
        toolkit.cprint_inspect(TTL_BALANCE_BTC)
        toolkit.cprint_inspect(TTL_BALANCE_USD)
        SPACE(vertical=1)
        LINE()
        LINE()

    else:
        SPACE(vertical=1)
        LINE()
        LINE()
        SPACE(vertical=1)
        toolkit.cprint(
             "        NO ARBITRAGE OPPORTUNITY            ",
            fg_color="ghostWhite",
            bg_color="magenta"
                        )

    if description=="bid_bal":
        toolkit.cprint(
            f"        NOT ENOUGH FUNDS @{top_bid_xch.upper():<8}         ",
            fg_color="gray",
            bg_color="darkGray"
                        )
        toolkit.quitter(True)
    if description=="ask_bal":
        toolkit.cprint(
            f"        NOT ENOUGH FUNDS @{top_ask_xch.upper():<8}         ",
            fg_color="gray",
            bg_color="darkGray"
                        )
    if description=="threshold":
        toolkit.cprint(
            "        DID NOT BREACH THRESHOLD",
            fg_color="gray",
            bg_color="darkGray"
                        )


def place_order(
    xch,
    base,
    quote,
    asset_amount
     ):
        create_trade_response = SK.client.create_trade(
            credentials.passport["Shrimpy"]["USER_ID"],
            credentials.passport["Shrimpy"]["ACCOUNTS"][xch],
            base,
            SK.safe_currency(quote, xch),
            asset_amount
        )
        print(
            credentials.passport["shrimpy"]["USER_ID"],
            credentials.passport["shrimpy"]["ACCOUNTS"][xch.lower()],
            base,
            SK.safe_currency(quote,  xch.lower()),
            asset_amount
        )
        return create_trade_response


# @DK.print_timing
def write_csv_data_to_disk(
    csv_file_path,
    run,
    headers,
    data_list
):
    if run > 0:
        data_array = [data_list]
        TK.CSVFilePrinter(
            csv_file_path,
            data_array,
        )
    else:
        data_array = [headers, data_list]
        TK.CSVFilePrinter(
            csv_file_path,
            data_array,
            WriteVsAppend="w"
        )

# @DK.print_timing


def arbitrage(now, run, orderbooks, toolkit, balance_values,  xch_status=[], spacer=""):

    orderbooks_N = sanitize_data(toolkit, orderbooks, GOODLIST)

    for idx, [sym, sym_data] in enumerate(orderbooks_N.items()):
        (
            base_syms,
            quote_syms,
            xchs,
            bid_prcs,
            bid_qtys,
            ask_prcs,
            ask_qtys
        ) = organize_data(sym_data)

        (
            base_sym,
            quote_sym,
            top_bid_xch,
            top_bid_prc_USD,

            top_bid_qty_BTC,

            top_ask_xch,
            top_ask_prc_USD,

            top_ask_qty_BTC

        ) = find_top_bid_ask(
            base_syms,
            quote_syms,
            xchs,
            bid_prcs,
            bid_qtys,
            ask_prcs,
            ask_qtys
        )

        (
            bid_acct_bal_BTC,
            bid_acct_bal_USD,
            ask_acct_bal_BTC,
            ask_acct_bal_USD
        ) = map_top_xch_to_balance(
            balance_values,
            top_bid_xch,
            top_ask_xch
            )

        # os.system("clear")

        top_bid_fee = calculate_fees(
            top_bid_xch
        )

        top_ask_fee = calculate_fees(
            top_ask_xch
        )

        (
            bid_inc_fees_USD,
            ask_inc_fees_USD,
            profit_inc_fees_USD
        ) = calculate_profit(
            top_bid_prc_USD,
            top_ask_prc_USD,
            top_bid_fee,
            top_ask_fee
        )

        (
       pro_rata_bid_USD,
       pro_rata_ask_USD,
       PRO_RATA_PROFIT_USD
        ) = update_profit(
            [
                bid_inc_fees_USD,
                ask_inc_fees_USD,
                profit_inc_fees_USD
            ]
        )
        
        global MAXPROFIT_USD
        MAXPROFIT_USD = update_maxprofit(PRO_RATA_PROFIT_USD, MAXPROFIT_USD)

        TTL_BALANCE_BTC = sum(balance_values[xch]["btcValue"]
                        for xch in balance_values)

        TTL_BALANCE_USD = sum(balance_values[xch]["usdValue"]
                        for xch in balance_values)        
        
        args_list = [toolkit, now, run, base_sym, quote_sym, top_bid_xch, top_ask_xch, bid_acct_bal_BTC, bid_acct_bal_USD, ask_acct_bal_BTC, ask_acct_bal_USD, top_bid_prc_USD, top_ask_prc_USD, top_bid_fee, top_ask_fee, bid_inc_fees_USD,    ask_inc_fees_USD, profit_inc_fees_USD, pro_rata_bid_USD, pro_rata_ask_USD, PRO_RATA_PROFIT_USD, TTL_BALANCE_BTC, TTL_BALANCE_USD]
        orders = [
            [
                    top_bid_xch,
                    base_sym,
                    quote_sym,
                    pro_rata_bid_BTC
            ],
            [
                    top_ask_xch,
                    quote_sym,
                    base_sym,
                    pro_rata_ask_USD
            ]
        ]

        if bid_acct_bal_BTC <= pro_rata_bid_BTC:
            proceed=False
            description="bid_bal"    
            args_list+=[proceed, description ]
            display_run(*args_list)
            toolkit.quitter(True)

        if ask_acct_bal_USD <= pro_rata_ask_USD:
            proceed=False
            description="ask_bal"  
            args_list+=[proceed, description ]
            display_run(*args_list)
            toolkit.quitter(True)
            
        if PRO_RATA_PROFIT_USD < THRESHOLD :
            proceed=False
            description="threshold"  
            args_list+=[proceed, description ]
            display_run(*args_list)
            # toolkit.quitter(True)
            
            
        if (
                PRO_RATA_PROFIT_USD > THRESHOLD and
                bid_acct_bal_BTC > pro_rata_bid_USD and
                ask_acct_bal_USD > pro_rata_ask_USD
            ):
                with multiprocessing.dummy.Pool(2) as pool:
                    results = pool.starmap(
                        place_order, [order_arg for order_arg in orders]
                    )
                print(tabulate(results))

                proceed=True
                description=None
                args_list+=[proceed,  description ]
                display_run(*args_list)
                
                args_list_headers =  [ "toolkit","now","run","base_sym","quote_sym","top_bid_xch","top_ask_xch","bid_acct_bal_BTC","bid_acct_bal_USD","ask_acct_bal_BTC","ask_acct_bal_USD","top_bid_prc_USD","top_ask_prc_USD","top_bid_fee","top_ask_fee","bid_inc_fees_USD","ask_inc_fees_USD","profit_inc_fees_USD","pro_rata_bid_USD","pro_rata_ask_USD","PRO_RATA_PROFIT_USD","TTL_BALANCE_BTC","TTL_BALANCE_US", "proceed", "description"]
                write_csv_data_to_disk(
                    CSV_FILE_PATH_PLACED,
                    run,
                    args_list_headers,
                    args_list
                )
                
                
                
                
                toolkit.quitter(True)

                            
        # else:
        #      display_run(*args_list)
                           
    args_list_headers =  [ "toolkit","now","run","base_sym","quote_sym","top_bid_xch","top_ask_xch","bid_acct_bal_BTC","bid_acct_bal_USD","ask_acct_bal_BTC","ask_acct_bal_USD","top_bid_prc_USD","top_ask_prc_USD","top_bid_fee","top_ask_fee","bid_inc_fees_USD","ask_inc_fees_USD","profit_inc_fees_USD","pro_rata_bid_USD","pro_rata_ask_USD","PRO_RATA_PROFIT_USD","TTL_BALANCE_BTC","TTL_BALANCE_US"]

                    
    write_csv_data_to_disk(
        CSV_FILE_PATH_NONE,
        run,
        args_list_headers,
        args_list
    )
        
        
        
        
        # display_run(
        #     toolkit,
        #     now,
        #     run,
        #     base_sym,
        #     quote_sym,
        #     top_bid_xch,
        #     top_ask_xch,
        #     bid_acct_bal_BTC,
        #     bid_acct_bal_USD,
        #     ask_acct_bal_BTC,
        #     ask_acct_bal_USD,
        #     top_bid_prc_USD,
        #     top_ask_prc_USD,
        #     top_bid_fee,
        #     top_ask_fee,
        #     bid_inc_fees_USD,   
        #     ask_inc_fees_USD,
        #     profit_inc_fees_USD,
        #     pro_rata_bid_USD,
        #     pro_rata_ask_USD,
        #     PRO_RATA_PROFIT_USD,
        #     TTL_BALANCE_BTC,
        #     TTL_BALANCE_USD,
        #     proceed=False,
        #    description=None
        #     )






        # ,top_bid_prc_USD, top_ask_prc_USD, top_bid_qty_BTC, top_ask_qty_BTC,MAXPROFIT,])

        # toolkit.multiprint(
        #     [_,top_bid_qty_BTC, top_ask_qty_BTC, _, , _, ask_acct_bal_BTC, ask_acct_bal_USD,_, qty_multiplier, _,])
        # ADJ_top_bid_prc_USD, ADJ_top_ask_prc_USD, ADJ_MAXPROFIT, ADJ_PROFIT = adjust_for_xch_qty(qty_multiplier,top_bid_qty_BTC, top_ask_qty_BTC, top_bid_prc_USD, top_ask_prc_USD, PROFIT)

        # create_trade_response = SK.client.create_trade(
        #     credentials.passport["Shrimpy"]["USER_ID"],
        #     credentials.passport["Shrimpy"]["ACCOUNTS"][top_bid_xch],
        #     "BTC",
        #     SK.safe_currency("USDT", top_bid_xch),
        #     asset_amount
        # )
        # bid = sell = from BTC = to USDT
        # ask = buy = from USDT = to BTC

        # SPACE(vertical=1)
        # toolkit.multiprint([ADJ_top_bid_prc_USD, ADJ_top_ask_prc_USD, ADJ_MAXPROFIT,])
        # toolkit.cprint_inspect(ADJ_PROFIT,fg_color=toolkit.create_truthy_index(ADJ_PROFIT)["fg_color"],bg_color=toolkit.create_truthy_index(ADJ_PROFIT)["bg_color"])
    
    

    


    # headers = ["now","run","base_sym","sym","top_bid_xch","top_ask_xch","top_bid_prc_USD","top_ask_prc_USD","top_bid_qty_BTC","top_ask_qty_BTC","bid_acct_bal_BTC","ask_acct_bal_BTC","bid_acct_bal_USD","ask_acct_bal_USD","qty_multiplier","MAXPROFIT","PROFIT","ADJ_top_bid_prc_USD","ADJ_top_ask_prc_USD","ADJ_MAXPROFIT","ADJ_PROFIT","TTL_BALANCE"]
    # data_list = [now,run,b_sym,sym,top_bid_xch,top_ask_xch,top_bid_prc_USD,top_ask_prc_USD,top_bid_qty_BTC,top_ask_qty_BTC,bid_acct_bal_BTC,ask_acct_bal_BTC,bid_acct_bal_USD,ask_acct_bal_USD,qty_multiplier,MAXPROFIT,PROFIT, ADJ_top_bid_prc_USD, ADJ_top_ask_prc_USD, ADJ_MAXPROFIT,ADJ_PROFIT,TTL_BALANCE]

    # write_csv_data_to_disk(csv_file_path, run,headers, data_list)
    # xch_status.append([PROFIT, ADJ_PROFIT])

    # print_form(form)("Sell {1} BTC on {} to receive {}")
    # print(f"Sell {1} BTC on {} to receive {}")
    # bid = sell = from BTC = to USDT
    # ask = buy = from USDT = to BTC


    return xch_status



# @DK.print_timing
def main():
    

    BALANCE_FLAG = True

    # TK.countdown(3)
    number_of_runs=input("How many consequetive runs:   ")
    delay=input("Delay between runs (secs):    ")
    for RUN in range(int(number_of_runs)):  # while True:
        os.system("clear")
        NOW = TK.create_timestamp(forfile=True)
        if BALANCE_FLAG:
            BALANCE_DICT = get_account_balances(SK, TK, GOODLIST)
            BALANCE_FLAG = False
        orderbooks = SK.fetch_orderbooks(
            EXCHANGES,  # exchange
            BASE_CURRENCY,  # base_sym # quote_sym # limit
        )

        arbitrage(NOW, RUN, orderbooks, TK, BALANCE_DICT)
        # print(BALANCE_DICT)
        TM.sleep(float(delay))

        


if __name__ == "__main__":
    main()
