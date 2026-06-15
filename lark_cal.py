#!/usr/bin/python3
"""
Lark Caclc. Based on the example from lark documentatiom.

"""
import lark
from lark import Lark, Transformer, v_args, lexer
import readline
import argparse

# We use decimal numbers instead of floats.
from decimal import *
getcontext().prec = 10

arg_calc_grammar = """
        ?start: sum
            | NAME "=" sum    -> assign_var

        ?sum: product
            | sum "+" product   -> add
            | sum "-" product   -> sub

        ?product: atom
            | product "*" atom  -> mul
            | product "/" atom  -> div

        ?atom: DECIMAL          -> number
            | "-" atom         -> neg
            | NAME             -> var
            | "(" sum ")"

        %import common.CNAME -> NAME
        %import common.NUMBER
        %import common.INT
        DECIMAL: PINT "," INT? | "," INT | PINT
        PINT: PDIGIT+  
        PDIGIT: "0".."9" | "."
        %import common.WS_INLINE

        %ignore WS_INLINE
    """


calc_grammar = """
        ?start: sum
            | NAME "=" sum    -> assign_var

        ?sum: product
            | sum "+" product   -> add
            | sum "-" product   -> sub

        ?product: atom
            | product "*" atom  -> mul
            | product "/" atom  -> div

        ?atom: DECIMAL          -> number
            | "-" atom         -> neg
            | NAME             -> var
            | "(" sum ")"

        %import common.CNAME -> NAME
        %import common.NUMBER
        %import common.INT
        DECIMAL: INT "." INT? | "." INT | INT
        %import common.WS_INLINE

        %ignore WS_INLINE
    """


class LDecimal: 
        def __init__(self, v,use_comma = False):
            #print("v=",v)
            #print("type=",type(v))
            if use_comma and type(v) is lark.lexer.Token:
                v = v.replace('.', '')
                v = v.replace(',', '.')
                #print("v=",v)
            self.value = Decimal(v)
        
        def __add__(self, op):
            return LDecimal(self.value + op.value)

        def __sub__(self, op):
            return LDecimal(self.value - op.value)

        def __mul__(self, op):
            return LDecimal(self.value * op.value)

        def __div__(self, op):
            return LDecimal(self.value / op.value)

        def __truediv__(self, op):
            return LDecimal(self.value / op.value)

        def __neg__(self):
            return LDecimal(-self.value)


@v_args(inline=True)  # Affects the signatures of the methods
class CalculateTree(Transformer):
        from operator import add, sub, mul, truediv as div, neg
        def __init__(self, use_comma=False):
            super().__init__()
            self.use_comma = use_comma
            self.vars = {}

        def number(self, token):
            return LDecimal(token, self.use_comma)

        def assign_var(self, name, value):
            self.vars[name] = value
            return value

        def var(self, name):
            try:
                return self.vars[name]
            except KeyError:
                raise Exception("Variable not found: %s" % name)

def make_calc(use_comma=False):
    grammar = arg_calc_grammar if use_comma else calc_grammar

    parser = Lark(
        grammar,
        parser="lalr",
        transformer=CalculateTree(use_comma)
    )

    return parser.parse



def main():
        
        parser = argparse.ArgumentParser(description="Lark Calc - Version 0.1.")
        parser.add_argument(
            "-c", "--comma", 
            action="store_true", 
            help="Use , for decimal separation)"
        )
        args = parser.parse_args()
        LDecimal.use_comma = args.comma

        if args.comma:
            decimal_separator=','
        else:
            decimal_separator='.'

        calc = make_calc(args.comma)

        print("Lark Calc - Version 0.1- decimal separator:",decimal_separator)
       
        while True:
            try:
                s = input('> ')
            except EOFError:
                break
            try:
                value = calc(s)
            except Exception as exc:
                print(exc)
                continue
            print(format_decimal(value,args.comma))


def test_sum():
        calc = make_calc(False)
        assert (calc("1+2").value == Decimal("3"))
        assert (calc("1.2+2").value == Decimal("3.2"))

def test_sum_arg():
        calc = make_calc(True)
        assert (calc("1+2").value == Decimal("3"))
        assert (calc("1,2+2").value == Decimal("3.2"))



def test_sub():
        calc = make_calc(False)
        assert (calc("12-3").value == Decimal(9))


def test_mult():
        calc = make_calc(False)
        assert (calc("2*2").value == Decimal(4))


def test_div():
        calc = make_calc(False)
        assert (calc("12/3").value == Decimal(4))


def test_neg():
       calc = make_calc(False)
       assert (calc("-3+5").value == Decimal(2))



def format_decimal(v, use_comma=False):
        if use_comma:
            #Convertir al formato argentino
            s = '{:,f}'.format(v.value)
            # si queremos 2 decimales
            # s = '{:,.2f}'.format(self.value)
            s = s.replace('.', '_')
            s = s.replace(',', '.')
            s = s.replace('_', ',')
        else: 
            s = str(v.value)
        return s


if __name__ == '__main__':
        main()
