#!/usr/bin/python3

from language import Instruction, Variable, Cmp
from interpreter import ExecutionState, Interpreter
from z3 import *


class SymbolicExecutionState(ExecutionState):
    def __init__(self, pc):
        super().__init__(pc)

        # add constraints here
        self.constraints = [True]
        # dont forget to create _copy_ of attributes
        # when forking states (i.e., dont use
        # new.attr = old.attr, that would
        # only create a reference)

    def write(self, var, value):
        assert isinstance(var, Variable)
        # in symbolic execution, value is expression, not int...
        assert isinstance(value, (ArithRef, IntNumRef, BoolRef))
        assert is_expr(value)
        self.variables[var] = value

    def eval(self, v):
        if isinstance(v, bool):
            return BoolVal(v) # convert int to z3 BoolVal
        # NOTE: this must be before IntVal, since True/False
        # match also IntVal
        if isinstance(v, int):
            return IntVal(v) # convert int to z3 IntVal
        assert isinstance(v, Instruction)
        return self.values.get(v)

    def copy(self):
        # must be overriden for symbolic execution
        # if you add new attributes
        n = SymbolicExecutionState(self.pc)
        n.constraints = self.constraints.copy()
        n.variables = self.variables.copy()
        n.values = self.values.copy()
        n.error = self.error
        return n

    def read(self, var):
        assert isinstance(var, Variable)
        return self.variables.get(var)

    def set(self, lhs, val):
        assert isinstance(lhs, Instruction)
        # in symbolic execution, val is expression, not int...
        assert isinstance(val, (ArithRef, IntNumRef, BoolRef))
        self.values[lhs] = val

    def __repr__(self):
        variables = {x.get_name() : v for (x, v) in self.variables.items()}
        values = {x.get_name() : v for (x, v) in self.values.items()}
        return f"[\n"\
               f"pc: {self.pc}\n"\
               f"variables: {variables}\n"\
               f"values: {values}\n"\
                "]"


class SymbolicExecutor(Interpreter):
    def __init__(self, program):
        super().__init__(program)
        self.executed_paths = 0
        self.errors = 0

    def executeMem(self, state):
        instruction = state.pc
        ty = instruction.get_ty()
        op = instruction.get_operand(0)
        if ty == Instruction.LOAD:
            value = state.read(op)
            if value is None:
                state.set(instruction, Int(op._name))
            else:
                state.set(instruction, value)
        elif ty == Instruction.STORE:
            value = state.eval(op)
            if value is None:
                state.error = f"Using unknown value: {op}"
            state.write(instruction.get_operand(1), value)
        else:
            raise RuntimeError(f"Invalid memory instruction: {instruction}")
        return state

    def executeArith(self, state):
        instruction = state.pc
        a = state.eval(instruction.get_operand(0))
        if a is None:
            state.error = f"Using unknown value: {instruction.get_operand(0)}"
            return state
        b = state.eval(instruction.get_operand(1))
        if b is None:
            state.error = f"Using unknown value: {instruction.get_operand(1)}"
            return state

        ty = instruction.get_ty()
        if ty == Instruction.ADD:
            result = a + b
        elif ty == Instruction.SUB:
            result = a - b
        if ty == Instruction.MUL:
            result = a * b
        if ty == Instruction.DIV:
            if b == 0:
                state.error = f"Division by 0: {instruction}"
                return state
            result = a / b

        state.set(instruction, result)

        return state

    def executePrint(self, state):
        instruction = state.pc

        vals = []
        for op in instruction.get_operands():
            val = state.eval(op)
            if val is None:
                state.error = f"Using unknown value: {op}"
                break

            vals.append(val)

        if vals:
           print(" ".join(map(str, vals)))

        return state

    def executeCmp(self, state):
        cmpinst = state.pc
        predicate = cmpinst.get_predicate()
        a = state.eval(cmpinst.get_operand(0))
        if a is None:
            state.error = f"Using unknown value: {cmpinst.get_operand(0)}"
            return state
        b = state.eval(cmpinst.get_operand(1))
        if b is None:
            state.error = f"Using unknown value: {cmpinst.get_operand(1)}"
            return state

        if predicate == Cmp.LT:
            result = a < b
        elif predicate == Cmp.LE:
            result = a <= b
        elif predicate == Cmp.GT:
            result = a > b
        elif predicate == Cmp.GE:
            result = a >= b
        elif predicate == Cmp.EQ:
            result = a == b
        elif predicate == Cmp.NE:
            result = a != b
        else:
            raise RuntimeError(f"Invalid comparison: {cmpinst}")

        state.set(cmpinst, result)

        return state

    def executeInstruction(self, state):
        instruction = state.pc
        ty = instruction.get_ty()
        print('executing:', instruction)

        if ty == Instruction.JUMP:
            return self.executeJump(state)

        if ty in [Instruction.ADD, Instruction.SUB,
                  Instruction.MUL, Instruction.DIV]:
            state = [self.executeArith(state)]
        elif ty in [Instruction.LOAD, Instruction.STORE]:
            state = [self.executeMem(state)]
        elif ty == Instruction.CMP:
            state = [self.executeCmp(state)]
        elif ty == Instruction.PRINT:
            state = [self.executePrint(state)]
        elif ty == Instruction.HALT:
            self.executed_paths += 1
            return [] # kill the execution
        elif ty == Instruction.ASSERT:
            state = self.executeAssert(state)
        else:
            raise RuntimeError(f"Unimplemented instruction: {instruction}")

        for i in state:
            if not i.error:
                i.pc = i.pc.get_next_inst()
                if not i.pc:
                    return []

        return state

    def executeJump(self, state):
        jump = state.pc
        sec_state = state.copy()

        def assign_block(op_branch_side, state_variation):
            successorblock = jump.get_operand(op_branch_side)
            state_variation.pc = successorblock[0]
            return state_variation

        condval = state.eval(jump.get_condition())
        if condval is None:
            state.error = f"Using unknown value: {jump.get_condition()}"
            return [state]
        state.constraints.append(condval)
        sec_state.constraints.append(Not(condval))
        s = Solver()

        condition = s.check(state.constraints)
        neq_condition = s.check(sec_state.constraints)

        if condition == sat and neq_condition == sat:
            return [assign_block(0, state), assign_block(1, sec_state)]
        elif condition == sat:
            return [assign_block(0, state)]
        elif neq_condition == sat:
            return [assign_block(1, sec_state)]

    def executeAssert(self, state):
        instruction = state.pc
        sec_state = state.copy()

        condval = state.eval(instruction.get_condition())
        if condval is None:
            state.error = f"Using unknown value!"
            return [state]
        state.constraints.append(condval)
        sec_state.constraints.append(Not(condval))
        s = Solver()

        condition = s.check(state.constraints)
        neq_condition = s.check(sec_state.constraints)

        if neq_condition == sat:
            self.errors += 1
            self.executed_paths += 1
            return []
        if condition == sat: return [state]
        if condition == unsat: return []

    def run(self):
        state_list = []
        entryblock = program.get_entry()

        state_list.append(SymbolicExecutionState(entryblock[0]))
        while state_list:
            item = state_list[-1]
            state_list.pop(-1)
            state_list = state_list + self.executeInstruction(item)
            if len(state_list) == 0:
                self.executed_paths = self.executed_paths + 1

        pass
        print(f"Executed paths: {self.executed_paths}")
        print(f"Error paths: {self.errors}")


if __name__ == "__main__":
    from parser import Parser
    from sys import argv
    if len(argv) != 2:
        print(f"Wrong numer of arguments, usage: {argv[0]} <program>")
        exit(1)
    parser = Parser(argv[1])
    program = parser.parse()
    if program is None:
        print("Program parsing failed!")
        exit(1)

    I = SymbolicExecutor(program)
    exit(I.run())
