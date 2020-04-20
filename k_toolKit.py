#!/usr/bin/env python3
# -*- coding: latin-1  -*-

# import ujson as json

import csv
import inspect
import os
import signal
import sys
import time as TM
from datetime import datetime as DT
from functools import wraps

import colorful as cf
import jsonpickle
import readchar
import ujson


import enums
import k_decoratorKit

# import json

cf.use_style("monokai")
DK = k_decoratorKit.Decoratorkit()


class Toolkit(object):
    "a set of helper methods"

    def __init__(self):
        self.i = 0
        self.create_color_index(
            fg0="lightGray", fg1="ghostWhite", bg0="darkGray", bg1="darkGray"
        )

    def JSON_file_reader(self, FilePath):
        with open(FilePath, "r", encoding="latin-1", errors="ignore") as f:
            jsonDictionary = jsonpickle.decode(f.read())
            return jsonDictionary

    def JSON_file_writer(self, FilePath, Data, WriteVsAppend="w"):
        with open(FilePath, WriteVsAppend) as f:
            f.write(jsonpickle.encode(Data))
        return 200

    def CSVFileReader(self, FilePath):
        with open(FilePath) as f:
            reader = csv.reader(f)
            csv_list = list(reader)
            return csv_list

    def CSVFilePrinter(self, FilePath, Data, WriteVsAppend="a"):
        try:
            with open(FilePath, "a", newline="") as outfile:
                csv_writer = csv.writer(outfile)
                csv_writer.writerows(Data)
                return 200
        except FileNotFoundError:
            open(FilePath, "w")
            return self.CSVFilePrinter(FilePath, Data)

    def HTMLFilePrinter(self, FilePath, Data, WriteVsAppend="w"):
        with open(FilePath, WriteVsAppend) as outfile:
            outfile.write(Data)
        return 200

    def create_timestamp(self, forfile=False):
        if forfile is True:
            return DT.now().strftime("%y_%m_%d__%H_%M_%S_%f")
        return DT.now().strftime("%y-%m-%d %H:%M:%S:%f")

    def define_path(self, file_path, timestamp, file_name):
        path = os.path.join(file_path, str(timestamp) + file_name + ".json")
        return path

    def multi_data2disk(self, timestamp, path, file_data_list, file_names_list):
        for idx, value in enumerate(file_names_list):
            file_path = self.define_path(path, timestamp, file_names_list[idx])
            data = file_data_list[idx]
            self.JSON_file_writer(file_path, data)
        return 200

    def count_files_in_dir(self, dirpath):

        directory = os.listdir(dirpath)
        return len(directory)

    def spacer(self, horizontal=0, vertical=0):
        if vertical:
            print("\n" * (vertical - 1))
        if horizontal:
            print(" " * horizontal)

    def format_to_precision(self, amount, precision=8):
        amount = float(amount)
        return float("{:0.0{}f}".format(amount, precision))

    def colorize(
        self, my_string, color="ghostWhite_on_darkGray", color_dict=enums.color_dict
    ):
        return color_dict[color](my_string)

    def style(self, style=cf.use_style("monokai")):
        return style

    def determine_number_cores(self):
        try:
            numProcessors = multiprocessing.cpu_count()
        except NotImplementedError:  # win32 environment variable NUMBER_OF_PROCESSORS not defined
            print("Cannot detect number of CPUs")
            numProcessors = 4
        return numProcessors

    def abort(self, expression=f"Botty go bye bye!"):
        # Abort logic, runs on exception
        sys.exit(expression)

    def print_timing(self, func):
        """
        create a timing decorator function
        use
        @print_timing
        just above the function you want to time
        """

        @wraps(func)  # improves debugging
        def wrapper(*arg, **kwarg):
            start = TM.perf_counter()  # needs python3.3 or higher
            result = func(*arg, **kwarg)
            end = TM.perf_counter()
            fs = "{} took {:.3f} microseconds"
            print(fs.format(func.__name__, (end - start) * 1000000))
            return result

        return wrapper

    def pprint(self, text_to_print, fg_on_bg=cf.ghostWhite_on_seaGreen):
        return fg_on_bg(text_to_print)

    def modulo(self, number):
        symbolA = "\u2588"
        symbolB = "\u2588"
        mod_dict = {True: symbolA, False: symbolB}
        return mod_dict[number % 2 == 0]

    def countdown(self, safety, start=50):
        if safety:
            symbolA = "\u2588"
            symbolB = "\u2588"
            leader = (symbolA + symbolB) * 25
            line = ""
            print("starting in: ")
            # print(cf.ghostWhite_on_green("\x1b[1A\x1b[2K"), flush=True)
            # print(f"3   ", flush=True, end="")
            print("", flush=True)
            TM.sleep(1)

            print(
                cf.ghostWhite_on_gray("\x1b[1A\x1b[2K"), flush=True,
            )
            print(f"3   ", flush=True, end="")
            TM.sleep(1)
            print(
                cf.ghostWhite_on_lightGray("\x1b[1A\x1b[2K"), flush=True,
            )
            print(f"2   ", flush=True, end="")
            TM.sleep(1)
            print(
                cf.ghostWhite_on_ghostWhite("\x1b[1A\x1b[2K"), flush=True,
            )
            print(f"1   ", flush=True, end="")
            TM.sleep(1)
            print(
                cf.ghostWhite_on_green("\x1b[1A\x1b[2K"), flush=True,
            )
            print(f"GO   ", flush=True)
            TM.sleep(1)
            return 200
        else:
            return None

    def key_continue(
        self, some_key=" ", msg="\rpress the SPACEBAR to comtimue or x to quit:"
    ):
        print(msg, end="", flush=True)
        s = readchar.readkey()
        if s == some_key:
            return
        elif s == "x":
            print(" quitting... ")
            sys.exit()
        self.key_continue()

    def create_directory(self, dir_name="data"):
        cwd = os.getcwd()
        dir_path = os.path.join(cwd, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        return 200

    def int2str(self, some_int, precision=8):
        return f"{some_int: {precision/10}f}"
        # print(cwd)
        # data_dir_path = os.path.join(cwd, data_dir_name)
        # os.makedirs(data_dir_path, exist_ok = True)
        # return data_dir_path

    # @DK.print_timing
    def create_named_dict_from_key(
        self, any_data=None, key=None, good_list=None, key_transformer=None
    ):
        """
        converts list of dictionaries to a dictionary of symbol : dictionary
        symbol is simultaneously converted from binance to its ccxt equivalent via lookup dict
        dict comprehension is fast
        get covers scenarios where key is not present in e2c dict
        """
        if good_list is not None:
            if key_transformer is not None:
                return {
                    key_transformer.get(item[key]): item
                    for item in any_data
                    if item[key] in good_list
                }
            return {item[key]: item for item in any_data if item[key] in good_list}

        else:
            if key_transformer is not None:
                return {key_transformer.get(item[key]): item for item in any_data}
            return {item[key]: item for item in any_data}

    def retrieve_name(self, var):
        """
            Gets the name of var. Does it from the out most frame inner-wards.
            :param var: variable to get name from.
            :return: string
            """
        for fi in reversed(inspect.stack()):
            names = [
                var_name
                for var_name, var_val in fi.frame.f_locals.items()
                if var_val is var
            ]
            if len(names) > 0:
                return names[0]

    def liner(
        self, symbol="\u2015", fg_color="gray",
    ):
        line = symbol * 44
        self.cprint(line, fg_color="gray")

    def cprint(
        self,
        my_string,
        fg_color="blue",
        bg_color="darkGray",
        end="\n",
        flush=True,
        invert=False,
    ):
        """print to std-out in color
        
        Arguments:
            my_string {str} -- the string you wish to print
        
        Keyword Arguments:
            fg_color {str} -- foreground color (default: {'darkGray'})
            bg_color {str} -- background color (default: {'purple'})
        """
        if bg_color:
            if not invert:
                pass
            else:
                fg_color, bg_color = bg_color, fg_color

            print(
                self.colorize(
                    f"   {my_string:<23} ", "_on_".join([fg_color, bg_color])
                ),
                flush=True,
                end=end,
            )

        else:
            print(self.colorize(f"   {my_string:<23} ", fg_color), flush=True, end=end)

    def create_truthy_index(self, truth):

        truth = self.isprofitable(truth)

        truthy_index = {
            True: {"fg_color": "darkGray", "bg_color": "green"},
            False: {"fg_color": "magenta", "bg_color": "darkGray"},
        }
        return truthy_index[truth]

    def color_palette(self, truth, index):
        color_dict = {
            True: {
                0: {"fg_color": "darkGray", "bg_color": "green"},
                1: {"fg_color": "gray", "bg_color": "green"},
            },
            False: {
                0: {"fg_color": "ghostWhite", "bg_color": "darkGray"},
                1: {"fg_color": "magenta", "bg_color": "darkGray"},
            },
        }
        return color_dict[truth][index]

    def isprofitable(self, truth):
        if truth <= 0:
            return False
        return True

    def cprint_inspect(
        self,
        my_variable,
        fg_color="blue",
        bg_color="darkGray",
        end="\n",
        flush=True,
        invert=False,
    ):
        try:
            self.cprint(
                f"{self.retrieve_name(my_variable):<18} {my_variable:>25.08f}",
                fg_color,
                bg_color,
                end,
                flush,
                invert,
            )
        except:
            try:
                self.cprint(
                    f"{self.retrieve_name(my_variable):<18} {my_variable:>25}",
                    fg_color,
                    bg_color,
                    end,
                    flush,
                    invert,
                )
            except Exception as e:
                print(e)
                print(my_variable)

    def create_color_index(
        self, fg0="yellow", fg1="green", bg0="magenta", bg1="orange"
    ):
        self.color_index = {
            "fg": {0: fg0, 1: fg1,},
            "bg": {0: bg0, 1: bg1,},
        }

    def multiprint(self, my_list, separator=None):  # u"\u2015"):
        for idx, item in enumerate(my_list):

            self.cprint_inspect(
                item,
                fg_color=self.color_index["fg"][idx % 2],
                bg_color=self.color_index["bg"][idx % 2],
            )

            if separator is not None:
                self.cprint(separator * 42, fg_color="gray", bg_color="darkGray")

    def quitter(self, flag=False):
        if flag == True:
            print("USER QUIT", flush=True)
            TM.sleep(0.25)
            os.kill(os.getpid(), signal.SIGUSR1)
            # sys.exit("dats da game")
        return "Not quitting"


if __name__ == "__main__":
    pass
