import sys
import antlr4
from interpreter.parse.HelloParser import HelloParser
from interpreter.parse.HelloLexer import HelloLexer
from interpreter.listener import OpListBuilder
from interpreter.program import Program


class ErrorListener(antlr4.error.ErrorListener.ErrorListener):
    def __init__(self):
        super(ErrorListener, self).__init__()
        self.errored_out = False

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errored_out = True


def main():
    # Parse the input file
    input_stream = antlr4.FileStream(sys.argv[1])

    lexer = HelloLexer(input_stream)
    token_stream = antlr4.CommonTokenStream(lexer)

    parser = HelloParser(token_stream)
    errors = ErrorListener()
    parser.addErrorListener(errors)
    tree = parser.program()

    if errors.errored_out:
        return

    # Walk the parse tree to build a list of Ops (analogous to an abstract
    # syntax tree)
    builder = OpListBuilder()
    tree.accept(builder)

    # Interpret the Op list
    program = Program(builder.ops)
    program.execute()


if __name__ == '__main__':
    main()
