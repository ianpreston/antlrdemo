import collections
import op


class Program(object):
    def __init__(self, ops):
        # The program's current "memory" state
        self.mem_idents = {}
        self.mem_addrs = collections.defaultdict(op.Value)

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

    def _memget_ident(self, ident):
        try:
            return self.mem_idents[ident]
        except KeyError:
            raise RuntimeError('Undefined ident: {}'.format(key))

    def _memget_addr(self, addr):
        res = self.resolve(addr.lvalue)
        return self.mem_addrs[res]

    def memget(self, key):
        if isinstance(key, op.Ident):
            return self._memget_ident(key)
        elif isinstance(key, op.MemAddr):
            return self._memget_addr(key)

    def memset(self, key, value):
        if isinstance(key, op.Ident):
            self.mem_idents[key] = value
        elif isinstance(key, op.MemAddr):
            res = self.resolve(key.lvalue)
            self.mem_addrs[res] = value

    def resolve(self, x):
        """
        Resolves an Ident, MemAddr, or Const to its current Value
        """
        if isinstance(x, op.Ident):
            return self.memget(x)
        elif isinstance(x, op.MemAddr):
            return self.memget(x)
        elif isinstance(x, op.Const):
            return op.Value(x)
        elif isinstance(x, op.Value):
            return x
        else:
            raise RuntimeError('Invalid argument to resolve(): {}'.format(x))

    def jmp(self, label_name):
        try:
            idx = self.labels[label_name]
            self.esp = idx
        except KeyError:
            raise RuntimeError('Undefined label: {}'.format(label_name))
