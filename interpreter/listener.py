from parse.HelloVisitor import HelloVisitor
import program
import op


class OpListBuilder(HelloVisitor):
    def __init__(self):
        super(OpListBuilder, self).__init__()
        self.ops = []

    def visitRvalue(self, ctx):
        lvalue = ctx.lvalue()
        if lvalue:
            return lvalue.accept(self)

        const = ctx.CONST()
        if const:
            return op.Const(const.getText())

    def visitLvalue(self, ctx):
        ident = ctx.IDENT()
        if ident:
            return op.Ident(ident.getText())

        mem = ctx.mem()
        if mem:
            mem_rvalue = mem.rvalue().accept(self)
            return op.MemAddr(mem_rvalue)

    def visitProgram(self, ctx):
        self.visitChildren(ctx)

    def visitStatement(self, ctx):
        self.visitChildren(ctx)

    def visitStmt_set(self, ctx):
        lvalue = ctx.lvalue().accept(self)
        rvalue = ctx.rvalue().accept(self)

        no = op.SetOp(
            lvalue=lvalue,
            rvalue=rvalue,
        )
        self.ops.append(no)

    def visitStmt_display(self, ctx):
        try:
            arg = ctx.rvalue().accept(self)
        except AttributeError:
            arg = ctx.STRING_LITERAL().getText().strip('"')
            arg = op.StringLiteral(arg)
        no = op.DispOp(arg)
        self.ops.append(no)

    def visitStmt_exec_unary(self, ctx):
        self.ops.append(self._handle_exec_stmt(ctx))

    def visitStmt_exec_binary(self, ctx):
        self.ops.append(self._handle_exec_stmt(ctx))

    def _handle_exec_stmt(self, ctx):
        func_name = ctx.IDENT().getText()

        result_lvalue = ctx.lvalue().accept(self)

        try:
            rvalue0 = ctx.rvalue(0)
            rvalue1 = ctx.rvalue(1)
        except TypeError:
            arg0 = ctx.rvalue().accept(self)
            arg1 = None
        else:
            arg0 = rvalue0.accept(self)
            arg1 = rvalue1.accept(self)

        return op.ExecOp(
            result_lvalue=result_lvalue,
            func_name=func_name,
            arg0=arg0,
            arg1=arg1,
        )

    def visitLabel(self, ctx):
        label_name = ctx.IDENT().getText()
        self.ops.append(op.LabelOp(label_name))

    def visitStmt_jumpif(self, ctx):
        condition = ctx.rvalue().accept(self)
        inverted = ctx.INVERT() is not None
        label_name = ctx.IDENT().getText()
        self.ops.append(op.JumpifOp(condition, inverted, label_name))

    def visitChildren(self, ctx):
        res = None
        for ci in xrange(ctx.getChildCount()):
            child = ctx.getChild(ci)
            res = child.accept(self)
        return res

    def visitTerminal(self, ctx):
        pass
