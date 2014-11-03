from parse.HelloListener import HelloListener
import program
import op


class OpListBuilder(HelloListener):
    def __init__(self):
        super(OpListBuilder, self).__init__()
        self.ops = []

    def _handle_exec_stmt(self, ctx):
        func_name = ctx.IDENT().getText()

        result_lvalue = self._handle_lvalue(ctx.lvalue())

        try:
            rvalue0 = ctx.rvalue(0)
            rvalue1 = ctx.rvalue(1)
        except TypeError:
            arg0 = self._handle_rvalue(ctx.rvalue())
            arg1 = None
        else:
            arg0 = self._handle_rvalue(rvalue0)
            arg1 = self._handle_rvalue(rvalue1)

        return op.ExecOp(
            result_lvalue=result_lvalue,
            func_name=func_name,
            arg0=arg0,
            arg1=arg1,
        )

    def _handle_rvalue(self, ctx):
        lvalue = ctx.lvalue()
        if lvalue:
            return self._handle_lvalue(lvalue)

        const = ctx.CONST()
        if const:
            return op.Const(const.getText())

    def _handle_lvalue(self, ctx):
        ident = ctx.IDENT()
        if ident:
            return op.Ident(ident.getText())

        mem = ctx.mem()
        if mem:
            mem_rvalue = self._handle_rvalue(mem.rvalue())
            return op.MemAddr(mem_rvalue)

    def enterStmt_set(self, ctx):
        lvalue = self._handle_lvalue(ctx.lvalue())
        rvalue = self._handle_rvalue(ctx.rvalue())

        no = op.SetOp(
            lvalue=lvalue,
            rvalue=rvalue,
        )
        self.ops.append(no)

    def enterStmt_display(self, ctx):
        try:
            arg = self._handle_rvalue(ctx.rvalue())
        except AttributeError:
            arg = ctx.STRING_LITERAL().getText().strip('"')
            arg = op.StringLiteral(arg)
        no = op.DispOp(arg)
        self.ops.append(no)

    def enterStmt_exec_unary(self, ctx):
        self.ops.append(self._handle_exec_stmt(ctx))

    def enterStmt_exec_binary(self, ctx):
        self.ops.append(self._handle_exec_stmt(ctx))

    def enterLabel(self, ctx):
        label_name = ctx.IDENT().getText()
        self.ops.append(op.LabelOp(label_name))

    def enterStmt_jumpif(self, ctx):
        condition = self._handle_rvalue(ctx.rvalue())
        inverted = ctx.INVERT() is not None
        label_name = ctx.IDENT().getText()
        self.ops.append(op.JumpifOp(condition, inverted, label_name))
