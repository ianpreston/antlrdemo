import operator


class Ident(str):
    pass


class Const(float):
    pass


class StringLiteral(str):
    pass


class Value(float):
    pass


class Op(object):
    def __init__(self):
        pass

    def execute(self, program):
        raise NotImplemented('Abstract base')


class SetOp(Op):
    def __init__(self, ident, value):
        super(SetOp, self).__init__()
        self.ident = ident
        self.value = value

    def execute(self, program):
        value = program.resolve(self.value)
        program.memset(self.ident, self.value)


class DispOp(Op):
    def __init__(self, arg):
        super(DispOp, self).__init__()
        self.arg = arg

    def execute(self, program):
        if isinstance(self.arg, Ident):
            print program.memget(self.arg)
        elif isinstance(self.arg, StringLiteral):
            print self.arg


class ExecOp(Op):
    def __init__(self, func_name, result_ident, arg0, arg1=None):
        self.result_ident = result_ident
        self.func_name = func_name
        self.arg0 = arg0
        self.arg1 = arg1

    def execute(self, program):
        func = getattr(operator, self.func_name)
        if not func:
            raise RuntimeError('No such function:', self.func_name)

        if self.arg1 is not None:
            result = func(
                program.resolve(self.arg0),
                program.resolve(self.arg1),
            )
        else:
            result = func(program.resolve(self.arg0))

        result = Value(result)
        program.memset(self.result_ident, result)


class LabelOp(Op):
    def __init__(self, label_name):
        self.label_name = label_name

    def execute(self, program):
        pass


class JumpifOp(Op):
    def __init__(self, condition, inverted, label_name):
        self.condition = condition
        self.inverted = inverted
        self.label_name = label_name

    def execute(self, program):
        truthy = bool(program.resolve(self.condition))
        if (truthy and not self.inverted) or (not truthy and self.inverted):
            program.jmp(self.label_name)
