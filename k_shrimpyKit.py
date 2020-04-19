import shrimpy
import credentials
import time as TM
import k_toolKit
import k_decoratorKit


# TK = k_toolKit.Toolkit()
# DK = k_decoratorKit.Decoratorkit()



class Shrimpykit(object):
    """ a bot for dealing with the Shrimpy Developers API"""

    def __init__(self, public_key, private_key):
        super(Shrimpykit, self).__init__()
        self.public_key = public_key
        self.private_key = private_key
        self.client = shrimpy.ShrimpyApiClient(self.public_key, self.private_key)
        
    
    
    
    # @DK.print_timing
    def prepare_exchange_parameter(self, exchanges):
        return ",".join(exchange for exchange in exchanges)
    
    # @DK.print_timing
    def safe_currency(self, currency=None, exchange=None):
        if currency is not None:
            if exchange is not None:
                if currency.upper() == "USDT":
                    if exchange.upper() == "HITBTC":
                        return "USD"
                    return "USDT"
            return currency.upper()
        return None

    # @DK.print_timing
    def fetch_orderbooks(
        self, exchanges, base_symbol=None, quote_symbol=None, limit=1
    ):  # limit):
        orderbooks = self.client.get_orderbooks(
            self.prepare_exchange_parameter(exchanges),
            self.safe_currency(base_symbol),
            self.safe_currency(quote_symbol),
            limit,
        )
        return orderbooks





def main():
    pass
    # public_key = credentials.passport["shrimpy"]["API_KEY"]
    # private_key = credentials.passport["shrimpy"]["API_SECRET"]
    # symbols = {
    #     "ada-btc": ["ada", "btc"],
    #     "ada-usdt": ["ada", "usdt"],
    #     "agi-btc": ["agi", "btc"],
    #     "amb-btc": ["amb", "btc"],
    #     "amb-eth": ["amb", "eth"],
    #     "atom-btc": ["atom", "btc"],
    #     "atom-usdt": ["atom", "usdt"],
    #     "bcd-btc": ["bcd", "btc"],
    #     "bnb-btc": ["bnb", "btc"],
    #     "bnb-usdt": ["bnb", "usdt"],
    #     "btc-pax": ["btc", "pax"],
    #     "btc-tusd": ["btc", "tusd"],
    #     "btc-usdc": ["btc", "usdc"],
    #     "btc-usdt": ["btc", "usdt"],
    #     "btt-usdt": ["btt", "usdt"],
    #     "chz-btc": ["chz", "btc"],
    #     "dash-btc": ["dash", "btc"],
    #     "dash-eth": ["dash", "eth"],
    #     "dash-usdt": ["dash", "usdt"],
    #     "dcr-btc": ["dcr", "btc"],
    #     "dent-eth": ["dent", "eth"],
    #     "elf-btc": ["elf", "btc"],
    #     "enj-btc": ["enj", "btc"],
    #     "enj-eth": ["enj", "eth"],
    #     "eos-btc": ["eos", "btc"],
    #     "eos-eth": ["eos", "eth"],
    #     "eos-usdt": ["eos", "usdt"],
    #     "etc-btc": ["etc", "btc"],
    #     "etc-eth": ["etc", "eth"],
    #     "etc-usdt": ["etc", "usdt"],
    #     "eth-btc": ["eth", "btc"],
    #     "eth-pax": ["eth", "pax"],
    #     "eth-tusd": ["eth", "tusd"],
    #     "eth-usdc": ["eth", "usdc"],
    #     "eth-usdt": ["eth", "usdt"],
    #     "fet-btc": ["fet", "btc"],
    #     "gas-btc": ["gas", "btc"],
    #     "gvt-eth": ["gvt", "eth"],
    #     "hot-btc": ["hot", "btc"],
    #     "iost-btc": ["iost", "btc"],
    #     "iotx-btc": ["iotx", "btc"],
    #     "key-btc": ["key", "btc"],
    #     "key-eth": ["key", "eth"],
    #     "knc-btc": ["knc", "btc"],
    #     "knc-eth": ["knc", "eth"],
    #     "loom-btc": ["loom", "btc"],
    #     "loom-eth": ["loom", "eth"],
    #     "lsk-btc": ["lsk", "btc"],
    #     "lsk-eth": ["lsk", "eth"],
    #     "ltc-btc": ["ltc", "btc"],
    #     "ltc-eth": ["ltc", "eth"],
    #     "ltc-usdt": ["ltc", "usdt"],
    #     "mana-btc": ["mana", "btc"],
    #     "mana-eth": ["mana", "eth"],
    #     "nano-btc": ["nano", "btc"],
    #     "nano-eth": ["nano", "eth"],
    #     "nano-usdt": ["nano", "usdt"],
    #     "nebl-btc": ["nebl", "btc"],
    #     "neo-btc": ["neo", "btc"],
    #     "neo-eth": ["neo", "eth"],
    #     "neo-usdt": ["neo", "usdt"],
    #     "omg-btc": ["omg", "btc"],
    #     "omg-eth": ["omg", "eth"],
    #     "one-btc": ["one", "btc"],
    #     "ont-btc": ["ont", "btc"],
    #     "ont-eth": ["ont", "eth"],
    #     "ont-usdt": ["ont", "usdt"],
    #     "powr-btc": ["powr", "btc"],
    #     "powr-eth": ["powr", "eth"],
    #     "ppt-btc": ["ppt", "btc"],
    #     "ppt-eth": ["ppt", "eth"],
    #     "qkc-btc": ["qkc", "btc"],
    #     "qkc-eth": ["qkc", "eth"],
    #     "qtum-btc": ["qtum", "btc"],
    #     "snt-btc": ["snt", "btc"],
    #     "snt-eth": ["snt", "eth"],
    #     "trx-btc": ["trx", "btc"],
    #     "trx-eth": ["trx", "eth"],
    #     "trx-usdt": ["trx", "usdt"],
    #     "vet-btc": ["vet", "btc"],
    #     "vet-eth": ["vet", "eth"],
    #     "vet-usdt": ["vet", "usdt"],
    #     "win-usdt": ["win", "usdt"],
    #     "wtc-btc": ["wtc", "btc"],
    #     "xem-btc": ["xem", "btc"],
    #     "xlm-btc": ["xlm", "btc"],
    #     "xlm-eth": ["xlm", "eth"],
    #     "xlm-usdt": ["xlm", "usdt"],
    #     "xmr-btc": ["xmr", "btc"],
    #     "xmr-eth": ["xmr", "eth"],
    #     "xrp-btc": ["xrp", "btc"],
    #     "xrp-eth": ["xrp", "eth"],
    #     "xrp-usdt": ["xrp", "usdt"],
    #     "xtz-btc": ["xtz", "btc"],
    #     "xtz-usdt": ["xtz", "usdt"],
    #     "zec-btc": ["zec", "btc"],
    #     "zec-usdt": ["zec", "usdt"],
    #     "zil-btc": ["zil", "btc"],
    #     "zrx-btc": ["zrx", "btc"],
    #     "zrx-eth": ["zrx", "eth"],
    # }
    # exchanges = ("binance", "hitbtc", "kucoin")
    # base_currency = "BTC"

    # shrimp_bot = ShrimpBot(public_key, private_key)
    
    # # s1 = TM.perf_counter()  

    # # orderbooks = shrimp_bot.fetch_orderbooks(
    # #     exchanges,  # exchange
    # #     "BTC",  
    # #     "PAX"    # base_symbol       # limit of how much depth to return on each side (bid & ask)
    # # )
    # # elapsed1 = TM.perf_counter() - s1
    
    # # TM.sleep(1)
    #     # print(orderbooks)
    # s2 = TM.perf_counter()  

    # orderbooks = shrimp_bot.fetch_orderbooks(
    #     exchanges,  # exchange
    #     "BTC",  
    #         # base_symbol       # limit of how much depth to return on each side (bid & ask)
    # )
    

if __name__ == "__main__":
    main()
