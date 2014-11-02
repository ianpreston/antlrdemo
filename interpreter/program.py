import op


class Program(object):
    def __init__(self, ops):
        # The program's "memory." All identifiers are global (there is no
        # scope). This dict maps Idents to their current Values.
        self.memory = {}

        # The "compiled" program, represented as a list of Op objects.
        self.ops = ops

        # Instruction pointer
        self.esp = 0

        # Map of label names to their Op index
        self.labels = {}
        self._map_labels()

    def _map_labels(self):
        for idx, current_op in enumerate(self.ops):
            if not isinstance(current_op, op.LabelOp):
                continue
            if current_op.label_name in self.labels.keys():
                raise RuntimeError(
                    'Redefinition of label: {}'.format(current_op.label_name)
                )
            self.labels[current_op.label_name] = idx

    def execute(self):
        while True:
            try:
                current_op = self.ops[self.esp]
            except IndexError:
                return

            current_op.execute(self)
            self.esp += 1

    def memget(self, ident):
        try:
            return self.memory[ident]
        except KeyError:
            raise RuntimeError('Identifier ref before set: {}'.format(ident))

    def memset(self, ident, value):
        self.memory[ident] = value

    def resolve(self, x):
        """
        Resolves an Ident or Const to its current Value
        """
        if isinstance(x, op.Ident):
            return self.memget(x)
        elif isinstance(x, op.Const):
            return op.Value(x)
        elif isinstance(x, op.Value):
            return x
        else:
            raise RuntimeError('Argument to resolve() must be Ident or Const')

    def jmp(self, label_name):
        try:
            idx = self.labels[label_name]
            self.esp = idx
        except KeyError:
            raise RuntimeError('Undefined label: {}'.format(label_name))
