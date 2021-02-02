# Created by PyCharm.
# Author: Jozef Vanický
# FI Login: xvanick1
# UČO: 506486
# Date: 2020-12-03
# Author's comment: -
# Verze Pythonu 3.8

import sys
import argparse


def err(text):
    print(text, file=sys.stderr)
    exit(10)


def __init__():
    ## Spracovanie vstupných argumentov
    input_file = sys.stdin
    parse_arguments(input_file)


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
                array = []
                i = 1
                with open(args.input) as f:
                    content = f.readlines()
                content = [line.strip() for line in content]
                i = 1
                for line in content:
                    line.replace(',', ('a' + str(i)))
                    i += 1

            except:
                err("Error: Input file not found or insufficient permissions!")

            try:
                f.close()
            except:
                err("Error: Closing CSV file failed!")
            print(content)
            # big_array = []
            # i = 1
            # for line in content:
            #     small_array = []
            #     temp = ""
            #     idx = 0
            #     for elem in line:
            #         temp = elem
            #         if elem != ',':
            #             if elem == 'a':
            #                 small_array.append(elem + str(i))
            #                 i += 1
            #             else:
            #                 if not elem.isdigit() and line[idx+1].isdigit():
            #                     small_array.append(elem + line[idx])
            #                 if elem.isdigit():
            #                     pass
            #                 else:
            #                     small_array.append(elem)
            #         idx += 1
            #     big_array.append(small_array)
            #     i += 1
            # print(big_array)

        exit()





__init__()
