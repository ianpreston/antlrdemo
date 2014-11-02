from parse.HelloListener import HelloListener
import program
import op


class OpListBuilder(HelloListener):
    def __init__(self):
        super(OpListBuilder, self).__init__()
        self.ops = []

    def _handle_exec_stmt(self, ctx):
        func_name = ctx.IDENT(0).getText()

        result_ident = ctx.IDENT(1).getText()
        result_ident = op.Ident(result_ident)

        try:
            arg0 = self._handle_rvalue(ctx.rvalue(0))
            arg1 = self._handle_rvalue(ctx.rvalue(1))
        except TypeError:
            # ctx.rvalue takes no arguments
            arg0 = self._handle_rvalue(ctx.rvalue())
            arg1 = None

        return op.ExecOp(
            result_ident=result_ident,
            func_name=func_name,
            arg0=arg0,
            arg1=arg1,
        )

    def _handle_rvalue(self, ctx):
        try:
            ident = ctx.IDENT().getText()
            ident = op.Ident(ident)
            return ident
        except AttributeError:
            const = ctx.CONST().getText()
            const = op.Const(const)
            return const

    def enterStmt_set(self, ctx):
        ident = ctx.IDENT().getText()
        rvalue = self._handle_rvalue(ctx.rvalue())

        no = op.SetOp(
            ident=op.Ident(ident),
            value=rvalue,
        )
        self.ops.append(no)

    def enterStmt_display(self, ctx):
        try:
            arg = ctx.IDENT().getText()
            arg = op.Ident(arg)
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
