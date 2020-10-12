from cmp import visitor
import ast


class FormatVisitor:
    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node: ast.ProgramNode, tabs):
        ans = '\t' * tabs + f'\\__ProgramNode'
        statements = '\n'.join(self.visit(child, tabs + 1) for child in node.declarations)
        return f'{ans}\n{statements}'

    @visitor.when(ast.ClassDeclarationNode)
    def visit(self, node: ast.ClassDeclarationNode, tabs):
        parent = '' if node.parent is None else f": {node.parent}"
        ans = '\t' * tabs + f'\\__ClassDeclarationNode: class {node.id} inherits {parent}'
        features = '\n'.join(self.visit(child, tabs + 1) for child in node.features)
        return f'{ans}\n{features}'

    @visitor.when(ast.AttrDeclarationNode)
    def visit(self, node: ast.AttrDeclarationNode, tabs=0):
        ans = '\t' * tabs + f'\\__AttrDeclarationNode: {node.id} : {node.typex}'
        expr = '\n' + self.visit(node.expression, tabs + 1) if node.expression is not None else ''
        return f'{ans}{expr}'

    @visitor.when(ast.MethodDeclarationNode)
    def visit(self, node: ast.MethodDeclarationNode, tabs=0):
        params = ', '.join(':'.join((param.id, param.typex)) for param in node.params)
        ans = '\t' * tabs + f'\\__MethodDeclarationNode: {node.id}({params}) : {node.type}'
        body = '\n' + self.visit(node.body, tabs + 1) if node.body is not None else ''
        return f'{ans}{body}'

    @visitor.when(ast.VarDeclarationNode)
    def visit(self, node: ast.VarDeclarationNode, tabs=0):
        ans = '\t' * tabs + f'\\__VarDeclarationNode: {node.id} : {node.typex}'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(ast.AssignNode)
    def visit(self, node: ast.AssignNode, tabs=0):
        ans = '\t' * tabs + f'\\__AssignNode: {node.id} = <expr>'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(ast.MethodCallNode)
    def visit(self, node: ast.MethodCallNode, tabs=0):
        obj = self.visit(node.expr, tabs + 1) if node.expr is not None else '\t' * (tabs + 1) + '\\__<obj> is None'
        typex = '@' + node.type if node.type is not None else ''
        ans = '\t' * tabs + f'\\__CallNode: <obj>{typex}.{node.id}(<expr>, ..., <expr>)'
        args = '\n'.join(self.visit(arg, tabs + 1) for arg in node.args)
        return f'{ans}\n{obj}\n{args}'

    @visitor.when(ast.ConditionalNode)
    def visit(self, node: ast.ConditionalNode, tabs=0):
        ans = '\t' * tabs + f'\\__ConditionalNode: if <expr> then <expr> else <expr> fi'
        condition = self.visit(node.condition, tabs + 1)
        then = self.visit(node.then_body, tabs + 1)
        elsex = self.visit(node.else_body, tabs + 1)
        return f'{ans}\n{condition}\n{then}\n{elsex}'

    @visitor.when(ast.LoopNode)
    def visit(self, node: ast.LoopNode, tabs=0):
        ans = '\t' * tabs + f'\\__LoopNode: while <expr> loop <expr> pool'
        condition = self.visit(node.condition, tabs + 1)
        body = self.visit(node.body, tabs + 1)
        return f'{ans}\n{condition}\n{body}'

    @visitor.when(ast.LetNode)
    def visit(self, node: ast.LetNode, tabs=0):
        ans = '\t' * tabs + f'\\__LetNode: let <vars-declaration-list> in <expr>'
        variables = '\n'.join(self.visit(arg, tabs + 1) for arg in node.var_decl_list)
        body = self.visit(node.in_expr, tabs + 1)
        return f'{ans}\n{variables}\n{body}'

    @visitor.when(ast.CaseNode)
    def visit(self, node: ast.CaseNode, tabs=0):
        ans = '\t' * tabs + f'\\__CaseNode: case <case-options-list> esac'
        case_options = '\n'.join(self.visit(case_option, tabs + 1) for case_option in node.options)
        expr = self.visit(node.case_expr, tabs + 1)
        return f'{ans}\n{expr}\n{case_options}'

    @visitor.when(ast.CaseOptionNode)
    def visit(self, node: ast.CaseOptionNode, tabs=0):
        ans = '\t' * tabs + f'\\__CaseOptionNode: {node.id}: {node.type} => <expr>'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(ast.BlocksNode)
    def visit(self, node: ast.BlocksNode, tabs=0):
        ans = '\t' * tabs + f'\\__BlocksNode:'
        expressions = '\n'.join(self.visit(expr, tabs + 1) for expr in node.expr_list)
        return f'{ans}\n{expressions}'

    @visitor.when(ast.IsVoidNode)
    def visit(self, node: ast.IsVoidNode, tabs=0):
        ans = '\t' * tabs + f'\\__IsVoidNode:'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(ast.NotNode)
    def visit(self, node: ast.NotNode, tabs=0):
        ans = '\t' * tabs + f'\\__NotNode:'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(ast.ComplementNode)
    def visit(self, node: ast.ComplementNode, tabs=0):
        ans = '\t' * tabs + f'\\__ComplementNode:'
        expr = self.visit(node.expr, tabs + 1)
        return f'{ans}\n{expr}'

    @visitor.when(ast.BinaryNode)
    def visit(self, node: ast.BinaryNode, tabs=0):
        ans = '\t' * tabs + f'\\__{node.__class__.__name__}:'
        left = self.visit(node.left, tabs + 1)
        right = self.visit(node.right, tabs + 1)
        return f'{ans}\n{left}\n{right}'

    @visitor.when(ast.AtomicNode)
    def visit(self, node: ast.AtomicNode, tabs=0):
        ans = '\t' * tabs + f'\\__{node.__class__.__name__}: {node.lex}'
        return f'{ans}'
