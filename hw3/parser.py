# Created by PyCharm.
# Author: Jozef Vanický
# FI Login: xvanick1
# UČO: 506486
# Date: 2020-12-03
# Author's comment: -
# Verze Pythonu 3.8

import sys
import argparse
import numpy


def err(text):
    print(text, file=sys.stderr)
    exit(10)


def __init__():
    ## Spracovanie vstupných argumentov
    input_file = sys.stdin
    parse_arguments(input_file)

    ## Načítanie inštrukcií z XML reprezentácie
    #self.xml_read()
    #self.parse_instructions()
    #self.instructions.sort(key=self.sort_order)


def parse_arguments(input_file):
    parser = argparse.ArgumentParser(
        description="Napoveda k parser.py. Parser vytvari spustitelny SMV model na zaklade vstupniho souboru "
                    "bludiste ve formatu CSV.",
        epilog="Ke spravne praci se skriptem musi byt zadan nasledujici argument.")
    parser.add_argument('-i', '--input', help='zdrojovy soubor bludiste ve formatu CSV',
                        required=True)

    if ("--help" in sys.argv) and len(sys.argv) > 2:
        err("Error: Wrong input!")
    try:
        args = parser.parse_args()
    except:
        if ("--help" in sys.argv) and len(sys.argv) == 2:
            exit(0)
        else:
            exit(10)  # no print !!!

    if not args.input:
        err("Error: --input required!")
    else:
        if args.input:
            try:
                with open(args.input) as f:
                    content = f.readlines()
                # you may also want to remove whitespace characters like `\n` at the end of each line
                content = [line.strip() for line in content]
                content = [line.replace(",,", ",a,") for line in content]
                content = [line.replace(",,", ",a,") for line in content]

            except:
                err("Error: Input file not found or insufficient permissions!")

            try:
                f.close()
            except:
                err("Error: Closing CSV file failed!")

            big_array = []
            i = 1
            for line in content:
                small_array = []
                j = 1
                temp = ""
                for elem in line:
                    print(type(elem))
                    if elem != ',':
                        if elem == 'a':
                            small_array.append(elem + str(i) + str(j))
                            j += 1
                        else:
                            temp = elem
                            if elem == 'd' or elem == 'k':
                                pass
                            if elem.isdigit():
                                small_array.append(temp + elem)
                            else:
                                small_array.append(elem)
                big_array.append(small_array)
                i += 1
            print(big_array)

        exit()





__init__()
