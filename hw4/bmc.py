#!/usr/bin/python

from bmcparsers.cmdparser import parse_cmd

# Choose which package you want to use: Z3 or pySMT
## --
from bmcparsers.z3parser import Z3Parser
from z3 import *
#from bmcparsers.pysmtparser import PySMTParser
#from pysmt.shortcuts import *


def subst_var_to_var_k(formulae, variables, k):
    for variable in variables:
        variable_k = Bool(str(variable) + str(k))
        formulae = substitute(formulae, (variable, variable_k))
    return formulae


def subst_var_to_var_nk(formulae, variables, k):
    for variable in variables:
        variable_nk = Bool(str(variable)[:-1] + str(k))
        formulae = substitute(formulae, (variable, variable_nk))
    return formulae


def bmc(maxk, xs, xns, prp, init, trans, backward = False, completeness = False):
    """
    Bounded model checking

    \param maxk           the upper bound on the number of iterations (path
                          length)
    \param xs             variables used in formulas
    \param xns            next-state variables used in formulas.
                          For a variable xs[i], the next-state variable is
                          xns[i].
    \param prp            property formula
    \param init           init relation formula
    \param trans          transition relation formula
    \param backward       set to True to perform the backward check
    \param completeness   set to True to perform completeness check
    """

    # Implement the BMC algorithm here
    k = 0
    s = Solver()
    history = []


    if backward:
        pass

        formulae = Not(prp)
        formulae = subst_var_to_var_k(formulae, xs, k)
        while True:
            pass

            '''Check max k reached'''
            if maxk is not None and k >= maxk:
                print(f"Unknown.")
                print(f"Finished with k={k}.")
                return False

            initial = subst_var_to_var_k(init, xs, k)
            formulae_to_check = And(formulae, initial)

            if sat == s.check(formulae_to_check):
                break

            temp = subst_var_to_var_k(trans, xs, k)
            temp = subst_var_to_var_nk(temp, xns, k + 1)

            formulae = And(formulae, temp)

            k += 1

        print(f"The property does not hold.")
        print(f"Finished with k={k}.")
        return True


    formulae = init
    formulae = subst_var_to_var_k(formulae, xs, k)
    if completeness:
        history.append(formulae)
    while True:
        pass

        '''Check max k reached'''
        if maxk is not None and k >= maxk:
            print(f"Unknown.")
            print(f"Finished with k={k}.")
            return False


        final = subst_var_to_var_k(prp, xs, k)
        final = Not(final)
        formulae_to_check = And(formulae, final)

        if sat == s.check(formulae_to_check):
            break

        temp = subst_var_to_var_k(trans, xs, k)
        temp = subst_var_to_var_nk(temp, xns, k + 1)

        if completeness:
            if temp in history:
                print(f"The property does hold.")
                print(f"Finished with k={k}.")
                return False
            history.append(temp)

        formulae = And(formulae, temp)
        k += 1

    print(f"The property does not hold.")
    print(f"Finished with k={k}.")
    return True

if __name__ == "__main__":
    from sys import argv
    from os.path import isfile

    args = parse_cmd()
    parser = Z3Parser()
    #parser = PySMTParser()

    maxk = args.maxk
    V, init, trans = parser.parseSystem(args.vars, args.init, args.trans)
    prp = parser.parseFormula(args.prp, V)

    print(
"""
Max k:                 {0}
Variables:             {1}
Next-state variables:  {2}
Init relation:
{3}
Transition relation:
{4}
Property:
{5}
Check completeness: {6}
Check backwards: {7}
""".format(maxk, ",".join(map(str, V.xs)), ",".join(map(str, V.xns)),
           str(init), str(trans), str(prp), args.completeness, args.backward)
)

    if init is None or trans is None:
        assert False, "Parsing the formulas failed"

    if args.dot is not None:
        from bmcparsers.dot import todot
        todot(args.dot, V, init, trans, prp)

    ###
    # Perform BMC
    ###
    print('--------------------------------')
    print('Running BMC')
    res = bmc(maxk, V.xs, V.xns, prp, init, trans, args.backward, args.completeness)

    exit(0 if res == True else 1)

