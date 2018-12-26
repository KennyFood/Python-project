#!/usr/bin/python
# -*- coding:utf8 -*-

import json
import networkx as nx
import matplotlib
import sys
import copy
from fractions import Fraction

reload(sys)
sys.setdefaultencoding('utf-8')
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

class Json_file():
    def __init__(self):
        pass


    def main(self):
        f = open('sample1.txt', 'r+')
        content = f.read()
        python_obj = json.loads(content)

        ## contract_list is contracts in source_code
        contract_list = []
        contract_list = self.get_contract_list(python_obj, contract_list)
        print "contract list length = " + str(len(contract_list)) + '\n'

        ## func_list is functions in one of the contracts above
        ## need to choose which function here
        func_list = []
        func_list = self.get_each_contract_func_list(contract_list[0], func_list)
        print "function list length = " + str(len(func_list)) +  '\n'

        ## choose function
        func = func_list[2]
        func_attributes = func['attributes']
        func_scope = func_attributes['visibility']

        ## function's input -> var
        input_list = []
        ## functions's output -> var
        output_list = []
        ## var in statements
        statement_list = []
        ## edges
        edge_list = []
        ## scope_dict
        scope_dict = {}
        ## partial order box
        edge_box = []

        # 主要解析函数
        self.get_every_var_in_func(func, statement_list, input_list, output_list, edge_list, scope_dict,edge_box)
        print 'This is private_scope_dict below:'
        print scope_dict
        print '---------------------------------'

        # 节点列表
        node_list = []
        self.merge_statementlist_to_nodelist(statement_list,node_list)

        # 创建有向图
        add_edges_list = []
        self.build_graph(input_list,output_list,node_list,edge_list,add_edges_list)

        print '^^^^^^^^^^^^^^^^^^^'
        for i in range(0, len(node_list)):
            print node_list[i]
        print '^^^^^^^^^^^^^^^^^^^'
        for i in range(0, len(add_edges_list)):
            print add_edges_list[i]
        print '^^^^^^^^^^^^^^^^^^^'

        ## 属性1: scope

        for i in range(0,len(node_list)):
            tmp = node_list[i]
            if(tmp not in scope_dict.keys()):
                scope_dict[tmp] = 'public'

        ## 属性2: partial order

        order = []
        self.simplify_edge_box(edge_box,order)
        print '**************'
        for i in range(0,len(order)):
            print order[i]

        ## partial order 每条边对应一个value
        order_dict = {}

        ## 滑窗大小
        window_size = 6
        self.build_order(order,add_edges_list,order_dict,window_size)

        #print order_dict
        print ' =========== '
        print order_dict
        print ' =========== '
        print scope_dict














    def get_target_value(self,key, dic, tmp_list):
        if not isinstance(dic, dict) or not isinstance(tmp_list, list):
            return 'argv[1] not an dict or argv[-1] not an list '

        if key in dic.keys():
            tmp_list.append(dic[key])
        else:
            for value in dic.values():
                if isinstance(value, dict):
                    self.get_target_value(key, value, tmp_list)
                elif isinstance(value, (list, tuple)):
                    self._get_value(key, value, tmp_list)
        return tmp_list

    def _get_value(self, key, val, tmp_list):
        for val_ in val:
            if isinstance(val_, dict):
                self.get_target_value(key, val_, tmp_list)
            elif isinstance(val_, (list, tuple)):
                self._get_value(key, val_, tmp_list)

    def get_contract_list(self, source_code, contract_list):

        contract_attributes = source_code['attributes']
        contract_names = contract_attributes['exportedSymbols']
        for key in contract_names.keys():
            print 'This is contract_list below: '
            print '------------------------'
            print key
            print '------------------------\n'


        contracts = source_code['children']
        for i in range(0, len(contracts)):
            contract_list.append(contracts[i])
        # print len(contract_list)
        return contract_list

    def get_each_contract_func_list(self, contract, func_list):

        i = 0
        tmp_list = contract['children']
        for i in range(0, len(tmp_list)):
            func_dict = tmp_list[i]
            if (func_dict['name'] == 'FunctionDefinition'):
                func_list.append(func_dict)
        return func_list

    def search_var_def_in_dict(self, dict, var_list,scope_dict):
        if ('name' in dict.keys() and dict['name'] == 'VariableDeclaration'):
            var_list.append(dict['attributes'])
            self.append_var_def_to_scope_dict(dict['attributes'],scope_dict)

    def append_var_def_to_scope_dict(self,var_dict,scope_dict):
        if(var_dict['type']!='bool'):
            var_name = var_dict['name']
            var_scope = 'private'
            scope_dict[var_name] = var_scope

    def search_func_call_in_dict(self, dict, func_call_list):
        if ('name' in dict.keys() and dict['name'] == "FunctionCall"):
            func_call_list.append(dict['attributes'])

    def search_identifier_in_dict(self, dict, identifier_list):
        if ('name' in dict.keys() and dict['name'] == "Identifier"):
            identifier_list.append(dict['attributes'])

    def search_statement_in_dict(self , dict, statement_list):
        if ('name' in dict.keys() and dict['name'] == "ExpressionStatement"):
            statement_list.append(dict['children'])

    def search_identifier_in_children_list(self , children_list, identifier_list):

        if (len(children_list) > 0):
            for i in range(0, len(children_list)):
                tmp_dict = children_list[i]
                if ('children' not in tmp_dict.keys()):
                    self.search_identifier_in_dict(tmp_dict, identifier_list)

                else:
                    self.search_identifier_in_dict(tmp_dict, identifier_list)
                    next_children_list = tmp_dict['children']
                    if (next_children_list != []):
                        self.search_identifier_in_dict(tmp_dict, identifier_list)
        else:
            print 'empty list'

    def search_var_in_children_list(self,children_list, var_list,scope_dict):

        if (len(children_list) > 0):
            for i in range(0, len(children_list)):
                tmp_dict = children_list[i]
                if ('children' not in tmp_dict.keys()):
                    self.search_var_def_in_dict(tmp_dict, var_list,scope_dict)
                    # search_identitier_in_dict( tmp_dict , identifier_list)

                else:
                    self.search_var_def_in_dict(tmp_dict, var_list,scope_dict)
                    # search_identitier_in_dict(tmp_dict, identifier_list)
                    next_children_list = tmp_dict['children']
                    if (next_children_list != []):
                        self.search_var_in_children_list(next_children_list, var_list,scope_dict)
                        # search_identitier_in_dict(tmp_dict, identifier_list)
        else:
            print 'empty list'

    def get_every_var_in_func(self,func, statement_list, input_list, output_list, edge_list,scope_dict,edge_box):

        if (func['children'] != []):
            children_list = func['children']

            input_dict = children_list[0]
            self.search_var_def_in_dict(input_dict, input_list,scope_dict)
            if ('children' in input_dict.keys() and input_dict['children'] != []):
                self.search_var_in_children_list(input_dict['children'], input_list,scope_dict)

            output_dict = children_list[1]
            self.search_var_def_in_dict(output_dict, output_list,scope_dict)
            if ('children' in output_dict.keys() and output_dict['children'] != []):
                self.search_var_in_children_list(output_dict['children'], output_list,scope_dict)

            block = children_list[2]
            i = 2
            print block['name']
            while (block['name'] != 'Block'):
                block = children_list[i + 1]
                print block['name']
            statements = block['children']

            ## handle block
            self.search_var_def_in_statements_list_and_handle_statements(statements, statement_list, edge_list,scope_dict,edge_box)

        else:
            print 'no children attributes in this function'

    def search_var_def_in_statements_list_and_handle_statements(self, statements, statement_list, edge_list,scope_dict,edge_box):
        identifier_list = []

        ## handle statements in block 1 by 1
        if (len(statements) > 0):
            for i in range(0, len(statements)):

                ## print 'this is statement ' + str(i)
                statement_dict = statements[i]

                type = statement_dict['name']

                if (type == 'VariableDeclarationStatement'):

                    ## VariableDeclaration + Assignment
                    if (len(statement_dict['children']) > 1):
                        # search_var_in_children_list(statement_dict['children'], statement_list)
                        # 形式等同于assignment ， 有左右两个child
                        # 这里把两个字典变成一个单独的列表进行处理，左边当做var_def处理，右边进行特殊处理
                        tmp = statement_dict['children']
                        var_def = []
                        var_def.append(tmp[0])
                        self.search_var_in_children_list(var_def, statement_list,scope_dict)
                        except_var_def = []
                        except_var_def.append(tmp[1])
                        self.handle_expression_statement(except_var_def, statement_list, identifier_list, edge_list)

                        # add edge

                        var = tmp[0]
                        var_attributes = var['attributes']
                        var_name = var_attributes['name']

                        ## add to scope_dict
                        #scope_dict[var_name] = 'private'

                        value = tmp[1]
                        if (value['name'] == 'Identifier'):
                            attributes = value['attributes']
                            right = attributes['value']
                            edge = (var_name, right)
                            edge_list.append(edge)
                        elif (value['name'] == 'IndexAccess'):
                            children = value['children']

                            left = children[0]
                            right = children[1]

                            left_attributes = left['attributes']
                            right_attributes = right['attributes']

                            if (right['name'] == 'MemberAccess'):
                                last_operation = 'IndexAccess'
                                tmp_list = []

                                self.Recursion_process(right, statement_list, identifier_list, edge_list, tmp_list, last_operation)

                                member = tmp_list[0]

                                statement_name = left_attributes['value'] + '[' + member['name'] + ']'
                                statement_dict = {'name': statement_name}
                                statement_list.append(statement_dict)

                                edge = (var_name, statement_name)
                                edge_list.append(edge)
                                tmp_box = copy.copy(edge_list)
                                edge_box.append(tmp_box)
                                return

                            left_name = 'left'
                            right_name = 'right'
                            if ('value' in left_attributes.keys()):
                                left_name = left_attributes['value']
                            elif ('name' in left_attributes.keys()):
                                left_name = left_attributes['name']

                            if ('value' in right_attributes.keys()):
                                right_name = right_attributes['value']
                            elif ('name' in right_attributes.keys()):
                                right_name = right_attributes['name']

                            statement_name = left_name + '[' + right_name + ']'
                            statement_dict = {'name': statement_name}
                            statement_list.append(statement_dict)

                            edge = (var_name, statement_name)
                            edge_list.append(edge)

                            # edge = (var_name, right)
                            # edge_list.append(edge)
                        elif (value['name'] == 'MemberAccess'):
                            attributes = value['attributes']
                            children = value['children']
                            member_name = attributes['member_name']
                            child = children[0]
                            child_attributes = child['attributes']
                            child_name = child['name']


                            if (child_name == 'IndexAccess'):
                                last_operation = 'MemberAccess'
                                left = child
                                left_tmp = []

                                self.Recursion_process(left, statement_list, identifier_list, edge_list, left_tmp, last_operation)
                                tmp_dict = left_tmp[0]
                                value_name = tmp_dict['name']
                            else:
                                value_name = child_attributes['value']
                            member = value_name + '.' + member_name
                            edge = (var_name, member)
                            edge_list.append(edge)
                            tmp_dict = {'name': member}
                            statement_list.append(tmp_dict)
                        elif (value['name'] == 'FunctionCall'):

                            children = value['children']
                            child = children[0]
                            child_attributes = child['attributes']
                            if ('value' in child_attributes.keys()):
                                value_name = child_attributes['value']

                                edge = (var_name, value_name)
                                edge_list.append(edge)
                            elif ('member_name' in child_attributes.keys()):
                                value_name = child_attributes['member_name']

                                edge = (var_name, value_name)
                                edge_list.append(edge)
                            else:
                                func_tmp_list = []
                                last_operation = 'FunctionCall'
                                self.Recursion_process(child, statement_list, identifier_list, edge_list, func_tmp_list, last_operation)
                                tmp = func_tmp_list[0]
                                if ('name' in tmp.keys()):
                                    tmp_name = tmp['name']
                                    edge = (var_name, tmp_name)
                                    edge_list.append(edge)
                                elif ('value' in tmp.keys()):
                                    tmp_name = tmp['value']
                                    edge = (var_name, tmp_name)
                                    edge_list.append(edge)
                                elif ('member_name' in tmp.keys()):
                                    tmp_name = tmp['member_name']
                                    edge = (var_name, tmp_name)
                                    edge_list.append(edge)
                                else:
                                    print "Variable FunctionCall defeat"
                        elif (value['name'] == 'BinaryOperation'):
                            children = value['children']
                            # binaryoperation has 2 children
                            left = children[0]
                            right = children[1]

                            left_tmp = []
                            right_tmp = []
                            var_tmp = []

                            last_operation = 'BinaryOperation'

                            self.Recursion_process(left, statement_list, identifier_list, edge_list, left_tmp, last_operation)
                            self.Recursion_process(right, statement_list, identifier_list, edge_list, right_tmp, last_operation)

                            self.append_left_and_right(left_tmp, right_tmp, var_tmp)

                            for i in range(0, len(var_tmp)):
                                tmp = var_tmp[i]
                                if ('name' in tmp.keys()):
                                    tmp_name = tmp['name']
                                    edge = (var_name, tmp_name)
                                    edge_list.append(edge)
                                elif ('value' in tmp.keys()):
                                    tmp_name = tmp['value']
                                    edge = (var_name, tmp_name)
                                    edge_list.append(edge)
                                else:
                                    print 'BinaryOperation defeat'

                        elif (value['name'] == 'UnaryOperation'):
                            children = value['children']
                            # binaryoperation has 1child
                            left = children[0]

                            left_tmp = []
                            right_tmp = []
                            var_tmp = []

                            last_operation = 'UnaryOperation'

                            self.Recursion_process(left, statement_list, identifier_list, edge_list, left_tmp, last_operation)

                            self.append_left_and_right(left_tmp, right_tmp, var_tmp)

                            for i in range(0, len(var_tmp)):
                                tmp = var_tmp[i]
                                if ('name' in tmp.keys()):
                                    tmp_name = tmp['name']
                                    edge = (var_name, tmp_name)
                                    edge_list.append(edge)
                                elif ('value' in tmp.keys()):
                                    tmp_name = tmp['value']
                                    edge = (var_name, tmp_name)
                                    edge_list.append(edge)
                                else:
                                    print 'BinaryOperation defeat'

                        tmp_box = copy.copy(edge_list)
                        edge_box.append(tmp_box)


                    else:
                        self.search_var_in_children_list(statement_dict['children'], statement_list,scope_dict)


                elif (type == 'ExpressionStatement'):
                    # print "in express"

                    self.handle_expression_statement(statement_dict['children'], statement_list, identifier_list, edge_list)
                    tmp_box = copy.copy(edge_list)
                    edge_box.append(tmp_box)


                elif (type == 'IfStatement'):
                    children_list = statement_dict['children']

                    if (len(children_list) == 3):
                        ## if else
                        condition = children_list[0]
                        last_operation = 'IfStatement'
                        var_tmp_list = []
                        self.Recursion_process(condition, statement_list, identifier_list, edge_list, var_tmp_list, last_operation)
                        tmp_box = copy.copy(edge_list)
                        edge_box.append(tmp_box)

                        seperate_sign = 'IfStatement'
                        edge_box.append(seperate_sign)
                        block1 = children_list[1]
                        self.search_var_def_in_statements_list_and_handle_statements(block1['children'], statement_list,edge_list,scope_dict,edge_box)
                        seperate_sign = 'End IfStatement'
                        edge_box.append(seperate_sign)

                        seperate_sign = 'Else'
                        edge_box.append(seperate_sign)
                        block2 = children_list[2]
                        self.search_var_def_in_statements_list_and_handle_statements(block2['children'], statement_list,edge_list,scope_dict,edge_box)
                        seperate_sign = 'End Else'
                        edge_box.append(seperate_sign)

                    elif (len(children_list) == 2):

                        condition = children_list[0]

                        if ('children' in condition.keys()):
                            ## if
                            statements_in_condition = condition['children']
                            # search_var_def_in_statements_list_and_handle_statements(statements_in_condition, statement_list, edge_list)
                            self.handle_expression_statement(statements_in_condition, statement_list, identifier_list,edge_list)
                            tmp_box = copy.copy(edge_list)
                            edge_box.append(tmp_box)

                        block = children_list[1]

                        if ('name' in block.keys() and block['name'] == 'Block'):
                            statements_in_if = block['children']
                            seperate_sign = 'IfStatement'
                            edge_box.append(seperate_sign)
                            self.search_var_def_in_statements_list_and_handle_statements(statements_in_if, statement_list, edge_list,scope_dict,edge_box)
                            seperate_sign = 'End IfStatement'
                            edge_box.append(seperate_sign)
                        else:
                            tmp_list = []
                            tmp_list.append(block)
                            seperate_sign = 'IfStatement'
                            edge_box.append(seperate_sign)
                            self.search_var_def_in_statements_list_and_handle_statements(tmp_list, statement_list, edge_list,scope_dict,edge_box)
                            seperate_sign = 'End IfStatement'
                            edge_box.append(seperate_sign)

                        # statements_in_if = block['children']
                        # search_var_def_in_statements_list_and_handle_statements(statements_in_if, statement_list, edge_list )

                elif (type == 'WhileStatement'):
                    children_list = statement_dict['children']

                    condition = children_list[0]
                    block = children_list[1]

                    statements_in_if = block['children']
                    seperate_sign = 'WhileStatement'
                    edge_box.append(seperate_sign)
                    self.search_var_def_in_statements_list_and_handle_statements(statements_in_if, statement_list, edge_list,scope_dict,edge_box)
                    seperate_sign = 'End WhileStatement'
                    edge_box.append(seperate_sign)

        # append_to_node_list(identifier_list , node_list)

        print '^^^^^^^'
        print_list = []
        print len(identifier_list)
        for i in range(0, len(identifier_list)):
            tmp = identifier_list[i]

            if (tmp not in print_list):

                if ('name' in tmp.keys()):
                    print tmp['name']
                elif ('value' in tmp.keys()):
                    print tmp['value']
                elif ('member_name' in tmp.keys()):
                    print tmp['member_name']
                else:
                    print 'cant find keys'
                print_list.append(tmp)
        print len(print_list)
        print '^^^^^^^^'

    def append_left_and_right(self,left_list, right_list, var_list):
        for i in range(0, len(left_list)):
            var_list.append(left_list[i])
        for i in range(0, len(right_list)):
            var_list.append(right_list[i])

    def handle_expression_statement(self,expression_list, statement_list, identifier_list, edge_list):
        # expressionstatement has only 1 children
        expression_dict = expression_list[0]
        # var_list =  identifier appears in this statement which only useful for previous expression
        var_list = []
        last_operation = 'start'
        self.Recursion_process(expression_dict, statement_list, identifier_list, edge_list, var_list, last_operation)

        ## ifstatement handle -> probably 2 children
        if (len(expression_list) == 2):
            expression_dict = expression_list[1]
            var_list = []
            last_operation = 'start'
            self.Recursion_process(expression_dict, statement_list, identifier_list, edge_list, var_list, last_operation)

    def Recursion_process(self,expression_dict, statement_list, identifier_list, edge_list, var_list, last_operation):
        operation = expression_dict['name']

        left_list = []
        right_list = []

        if (operation == 'Assignment'):
            children = expression_dict['children']
            # assigment has 2 children : left and right
            last_operation = 'Assignment'
            left_children_dict = children[0]
            self.Recursion_process(left_children_dict, statement_list, identifier_list, edge_list, left_list, last_operation)
            right_children_dict = children[1]
            self.Recursion_process(right_children_dict, statement_list, identifier_list, edge_list, right_list,
                              last_operation)

            self.append_left_and_right(left_list, right_list, var_list)

            self.add_assignment_edges(left_list, right_list, edge_list)
            # print '----------'
            # print var_list
            # print left_list
            # print right_list
            # print identifier_list
            # print '----------'
        elif (operation == 'FunctionCall'):

            children = expression_dict['children']
            last_operation = 'FunctionCall'
            # functioncall has 2 children : itself and argument
            itself = children[0]
            self.Recursion_process(itself, statement_list, identifier_list, edge_list, left_list, last_operation)

            # more than 1 argument
            for i in range(1, len(children)):
                argument = children[i]
                last_operation = 'Argument'
                self.Recursion_process(argument, statement_list, identifier_list, edge_list, right_list, last_operation)

            self.append_func_call_left_right(left_list, right_list, var_list)
            if (len(left_list) > 0):
                statement_list.append(left_list[0])
                self.add_functioncall_edges(left_list, right_list, edge_list)
            # print '----------'
            # print var_list
            # print left_list
            # print right_list
            # print identifier_list
            # print '----------'
        elif (operation == 'TupleExpression'):
            children = expression_dict['children']
            last_operation = 'TupleExpression'
            #self.search_identifier_in_children_list(children, var_list)
            #self.search_identifier_in_children_list(children, identifier_list)
            for i in range(0,len(children)):
                tmp = children[i]
                tmp_list = []
                self.Recursion_process(tmp,statement_list,identifier_list,edge_list,tmp_list,last_operation)
                self.append_left_and_right(tmp_list,right_list,var_list)

            return
        elif (operation == 'Identifier'):

            if (last_operation == 'IndexAccess'):
                var_list.append(expression_dict['attributes'])
                identifier_list.append(expression_dict['attributes'])
                return

            var_list.append(expression_dict['attributes'])
            identifier_list.append(expression_dict['attributes'])

            statement_list.append(expression_dict['attributes'])
            return
        elif (operation == 'MemberAccess'):
            # 如果是Func call类型的MemberAccess

            if (last_operation == 'FunctionCall'):

                attributes = expression_dict['attributes']
                member_name = attributes['member_name']

                last_operation = 'MemberAccess'
                children = expression_dict['children']
                child = children[0]
                self.Recursion_process(child, statement_list, identifier_list, edge_list, left_list, last_operation)

                var_list.append(expression_dict['attributes'])
                identifier_list.append(expression_dict['attributes'])
                # statement_list.append(expression_dict['attributes'])

                for i in range(0, len(left_list)):
                    tmp_dict = left_list[i]
                    if ('value' in tmp_dict.keys() and tmp_dict['value'] == 'msg'):
                        _member = 'msg' + '.' + member_name
                        _dict = {'name': _member}
                        var_list.append(_dict)
                    else:
                        var_list.append(tmp_dict)

                '''
                if(len(left_list) == 0):
                    print "MemberAccess failed"
                    return error
                else:
                    tmp_dict = left_list[0]
                    if('value' in tmp_dict.keys()):
                        _member = tmp_dict['value'] + '.' + member_name
                        _dict = {'name': _member}
                        var_list.append(_dict)
                        identifier_list.append(_dict)
                        edge = (_member,member_name)
                        edge_list.append(edge)
                    else:
                        var_list.append(tmp_dict)
                '''

                return
            elif (last_operation == 'Argument'):
                children = expression_dict['children']
                last_operation = 'MemberAccess'

                attributes = expression_dict['attributes']
                member_name = attributes['member_name']

                self.Recursion_process(children[0], statement_list, identifier_list, edge_list, left_list, last_operation)
                # statement_list.append(expression_dict['attributes'])

                if (len(left_list) == 0):
                    print "MemberAccess failed"
                    return
                else:
                    tmp_dict = left_list[0]
                    if ('value' in tmp_dict.keys()):
                        _member = tmp_dict['value'] + '.' + member_name
                        _dict = {'name': _member}
                        var_list.append(_dict)
                        statement_list.append(_dict)
                        # edge = (_member,member_name)
                        # edge_list.append(edge)
                    else:
                        var_list.append(tmp_dict)

                return
            # 如果是赋值类型的MemberAccess
            elif (last_operation == 'Assignment' or last_operation == 'IndexAccess' or last_operation == 'BinaryOperation'):
                children = expression_dict['children']
                last_operation = 'MemberAccess'

                attributes = expression_dict['attributes']
                member_name = attributes['member_name']

                self.Recursion_process(children[0], statement_list, identifier_list, edge_list, left_list, last_operation)

                for i in range(0, len(left_list)):
                    tmp_dict = left_list[i]
                    if ('value' in tmp_dict.keys()):
                        _member = tmp_dict['value'] + '.' + member_name
                        _dict = {'name': _member}
                        var_list.append(_dict)
                        statement_list.append(_dict)
                    else:
                        var_list.append(left_list[i])
                        statement_list.append(left_list[i])
            elif (last_operation == 'MemberAccess'):
                ## from here

                attributes = expression_dict['attributes']
                children = expression_dict['children']

                last_operation = 'MemberAccess'
                child = children[0]
                self.Recursion_process(child, statement_list, identifier_list, edge_list, left_list, last_operation)

                ## to here

                # attributes = expression_dict['attributes']
                # children = expression_dict['children']
                member_name = attributes['member_name']
                # child = children[0]
                # child_attributes = child['attributes']

                ## here
                child_dict = left_list[0]
                # print child_dict
                if ('name' in child_dict.keys()):
                    value_name = child_dict['name']
                elif ('value' in child_dict.keys()):
                    # child_attributes = child_dict['attributes']
                    value_name = child_dict['value']
                else:
                    value_name = 'error'
                ##to here
                # child_attributes = child_dict['attributes']
                # value_name = child_attributes['value']
                member = value_name + '.' + member_name
                tmp_dict = {'name': member}
                statement_list.append(tmp_dict)
                var_list.append(tmp_dict)

                edge = (member, value_name)
                edge_list.append(edge)

            # elif(last_operation == 'BinaryOperation')





        elif (operation == 'IndexAccess'):
            children = expression_dict['children']
            left_children_dict = children[0]
            right_children_dict = children[1]
            # 跟上一层交互只有indexaccess字典里，children中左节点，因为它包含的左边也就是数组信息，右边包含index信息

            # var_list包含和上一层交互的identifier信息
            # var_list.append(left['attributes'])

            # 将左右identifier都要放入func所有identifier列表--> identifier_list中
            identifier_list.append(left_children_dict['attributes'])
            identifier_list.append(right_children_dict['attributes'])

            # ---------
            # left_attributes = left_children_dict['attributes']
            # right_attributes = right_children_dict['attributes']

            # ---------
            last_operation = 'IndexAccess'
            self.Recursion_process(left_children_dict, statement_list, identifier_list, edge_list, left_list, last_operation)
            self.Recursion_process(right_children_dict, statement_list, identifier_list, edge_list, right_list,
                              last_operation)
            left = left_list[0]
            right = right_list[0]

            left_name = left['value']
            if ('value' in right.keys()):
                right_name = right['value']
            elif ('name' in right.keys()):
                right_name = right['name']
            else:
                print 'invalid index'
                return
            statement_name = left_name + '[' + right_name + ']'
            statement_dict = {'name': statement_name}
            statement_list.append(statement_dict)

            var_list.append(statement_dict)

            edge = (statement_name, right_name)
            edge_list.append(edge)

            return

            # ---------
            '''
            # IndexAccess加边逻辑

            #edge = (left_attributes['value'] , right_attributes['value'])
            #edge_list.append(edge)

            # 构造一个index的形式加入到statement_list中
            statement_name = left_attributes['value'] + '[' + right_attributes['value'] + ']'
            statement_dict = {'name' : statement_name}
            statement_list.append(statement_dict)

            #var_list包含和上一层交互的identifier信息
            var_list.append(statement_dict)

            # IndexAccess加边逻辑

            edge = (statement_name, right_attributes['value'])
            edge_list.append(edge)

            return
            '''
        elif (operation == 'Literal'):
            if (last_operation == 'Assignment'):
                var_list.append(expression_dict['attributes'])
            elif (last_operation == 'IndexAccess'):
                var_list.append(expression_dict['attributes'])

        elif (operation == 'BinaryOperation'):
            children = expression_dict['children']
            # binaryoperation has 2 children
            left_children_dict = children[0]
            right_children_dict = children[1]

            last_operation = 'BinaryOperation'

            self.Recursion_process(left_children_dict, statement_list, identifier_list, edge_list, left_list, last_operation)
            self.Recursion_process(right_children_dict, statement_list, identifier_list, edge_list, right_list,
                              last_operation)

            self.append_left_and_right(left_list, right_list, var_list)

        elif (operation == 'UnaryOperation'):
            children = expression_dict['children']
            # "UnaryOperation" seems it has 1 child
            children_dict = children[0]

            last_operation = 'UnaryOperation'

            self.Recursion_process(children_dict, statement_list, identifier_list, edge_list, left_list, last_operation)

            self.append_left_and_right(left_list, right_list, var_list)





        else:
            return

    def add_assignment_edges(self,left_list, right_list, edge_list):
        for i in range(0, len(left_list)):
            tmp = left_list[i]
            if ('value' in tmp.keys()):
                tmp_name = tmp['value']
            elif ('name' in tmp.keys()):
                tmp_name = tmp['name']
            else:
                print 'no assgiment value '
                return
            for i in range(0, len(right_list)):
                next_tmp = right_list[i]
                if ('value' in next_tmp.keys()):
                    next_tmp_name = next_tmp['value']
                    edge = (tmp_name, next_tmp_name)
                    edge_list.append(edge)
                elif ('member_name' in next_tmp.keys()):
                    next_tmp_name = next_tmp['member_name']
                    edge = (tmp_name, next_tmp_name)
                    edge_list.append(edge)
                elif ('name' in next_tmp.keys()):
                    next_tmp_name = next_tmp['name']
                    edge = (tmp_name, next_tmp_name)
                    edge_list.append(edge)

    def add_functioncall_edges(self,left_list, right_list, edge_list):
        func_self = left_list[0]
        if ('member_name' in func_self.keys()):
            func_name = func_self['member_name']
        elif ('value' in func_self.keys()):
            func_name = func_self['value']
        else:
            print 'cant find func_name'
            return
        for i in range(1, len(left_list)):
            tmp = left_list[i]
            if ('value' in tmp.keys()):
                tmp_name = tmp['value']
                edge = (func_name, tmp_name)
                edge_list.append(edge)
            elif ('name' in tmp.keys()):
                tmp_name = tmp['name']
                edge = (func_name, tmp_name)
                edge_list.append(edge)
            elif ('member_name' in tmp.keys()):
                tmp_name = tmp['member_name']
                edge = (func_name, tmp_name)
                edge_list.append(edge)

        for i in range(0, len(right_list)):
            tmp = right_list[i]
            if ('value' in tmp.keys()):
                tmp_name = tmp['value']
                edge = (func_name, tmp_name)
                edge_list.append(edge)
            elif ('name' in tmp.keys()):
                tmp_name = tmp['name']
                edge = (func_name, tmp_name)
                edge_list.append(edge)
            elif ('member_name' in tmp.keys()):
                tmp_name = tmp['member_name']
                edge = (func_name, tmp_name)
                edge_list.append(edge)

    def append_func_call_left_right(self,left_list, right_list, var_list):
        ## function call 传送给前一个Recursion的值只有代表它自己的节点 -> left_list的第一个元素
        if (len(left_list) > 0):
            func_self = left_list[0]
            var_list.append(func_self)
        else:
            func_self = {'name': 'error', 'value': 'error'}
            var_list.append(func_self)

    def append_to_node_list(self,dict_list, append_list):

        for i in range(0, len(dict_list)):
            tmp = dict_list[i]

            if ('name' in tmp.keys()):

                tmp_name = tmp['name']
                if (tmp_name not in append_list):
                    append_list.append(tmp_name)

            elif ('value' in tmp.keys()):
                print '333'
                tmp_name = tmp['value']
                if (tmp_name not in append_list):
                    append_list.append(tmp_name)

    def merge_statementlist_to_nodelist(self,statement_list,node_list):
        for i in range(0, len(statement_list)):
            tmp = statement_list[i]

            if ('name' in tmp.keys()):

                print_name = tmp['name']
                if (print_name not in node_list):
                    node_list.append(print_name)
            elif ('value' in tmp.keys()):
                print_name = tmp['value']
                if (print_name not in node_list):
                    node_list.append(print_name)
            elif ('member_name' in tmp.keys()):
                print_name = tmp['member_name']
                if (print_name not in node_list):
                    node_list.append(print_name)

    def merge_lists_to_nodelist(self,input_or_output_list, node_list):
        for i in range(0, len(input_or_output_list)):
            tmp = input_or_output_list[i]

            if ('name' in tmp.keys()):

                print_name = tmp['name']
                if (print_name not in node_list):
                    node_list.append(print_name)
            elif ('value' in tmp.keys()):
                print_name = tmp['value']
                if (print_name not in node_list):
                    node_list.append(print_name)
            elif ('member_name' in tmp.keys()):
                print_name = tmp['member_name']
                if (print_name not in node_list):
                    node_list.append(print_name)

    def build_graph(self, input_list , output_list , node_list , edge_list , add_edges_list):
        self.merge_statementlist_to_nodelist(input_list, node_list)
        self.merge_statementlist_to_nodelist(output_list, node_list)
        if ('msg' in node_list):
            node_list.remove('msg')

        # length = len(print_list)
        # print length
        # print print_list
        # matrix = [[0 for i in range(length)] for i in range(length)]

        remove_list = []

        for i in range(0, len(edge_list)):
            tmp = edge_list[i]
            left_tmp = tmp[0]
            right_tmp = tmp[1]
            if (right_tmp == 'msg.value'):
                edge = (left_tmp, 'value')
                remove_list.append(edge)

            if (right_tmp == 'msg.sender'):
                edge = (left_tmp, 'sender')
                remove_list.append(edge)

            if (left_tmp == 'msg.value' or right_tmp == 'msg.value'):
                if ('msg.value' not in node_list):
                    node_list.append('msg.value')

        length = len(node_list)
        print length
        print node_list
        matrix = [[0 for i in range(length)] for i in range(length)]

        for i in range(0, len(remove_list)):
            tmp = remove_list[i]
            try:
                edge_list.remove(tmp)
            except:
                print "remove defeat"

        for i in range(0, len(edge_list)):
            tmp = edge_list[i]
            left = tmp[0]
            right = tmp[1]

            if (left in node_list and right in node_list):
                j = node_list.index(left)
                k = node_list.index(right)
                matrix[j][k] = 1
                add_edges_list.append(tmp)
            else:
                print "invalid edge " + str(i)

        ## check print_list and add_edges_list
        print 'this is print_list below'
        print node_list
        print len(node_list)
        print '------------'
        print 'this is final edge_list below'
        print add_edges_list
        print len(add_edges_list)
        print '------------'

        for i in range(0, length):
            print matrix[i]

        G = nx.DiGraph()
        G.add_nodes_from(node_list)
        G.add_edges_from(add_edges_list)
        # position = nx.random_layout(G)
        # position = nx.spring_layout(G)
        position = nx.circular_layout(G)
        nx.draw(G, position, with_labels='True', style='dashed', node_size=400, node_color='g', font_size=9,
                font_color='black', width=4, edge_color='b')
        plt.show()

    def simplify_edge_box(self,edge_box,order):
        last = []
        for i in range(0,len(edge_box)):
            tmp1 = edge_box[i]
            #tmp2 = edge_box[i+1]
            #if((tmp1 != 'IfStatement' and tmp1 != 'End IfStatement' and tmp1 != 'Else' and tmp1 != 'End Else' and tmp1 != 'WhileStatement' and tmp1 != 'End WhileStatement') and (tmp2 != 'IfStatement' and tmp2 != 'End IfStatement' and tmp2 != 'Else' and tmp2 != 'End Else' and tmp2 != 'WhileStatement' and tmp2 != 'End WhileStatement')):
            if(tmp1 != 'IfStatement' and tmp1 != 'End IfStatement' and tmp1 != 'Else' and tmp1 != 'End Else' and tmp1 != 'WhileStatement' and tmp1 != 'End WhileStatement'):
                ret = []
                for j in range(len(last),len(tmp1)):
                    if(tmp1[j] not in ret):
                        ret.append(tmp1[j])
                order.append(ret)
                last = tmp1
            else:
                order.append(tmp1)

    def build_order(self,order,add_edges_list,order_dict,window_size):
        # initialize dict
        for i in range(0,len(add_edges_list)):
            key = add_edges_list[i]
            value = 1
            order_dict[key] = value

        # calculate partial order
        for i in range(0,len(order)):
            tmp = order[i]
            if(self.sensetive_operation(tmp)):
                ## forward calculate
                length = i - window_size
                if(length>0):
                    self.calculate_forward(order,add_edges_list,order_dict,i,1)
                    return



    def sensetive_operation(self,order_list):
        if(isinstance(order_list,list)):
            for i in range(0,len(order_list)):
                tmp = order_list[i]
                left = tmp[0]
                right = tmp[1]
                if(left == 'send' or right == 'send'):
                    return True
        else:
            return False

    def calculate_forward(self,order,add_edges_list,order_dict,index,number):
        current_group = order[index]
        next_group = order[index-number]
        if(isinstance(next_group,list)):
            length1 = 0
            length2 = 0

            for i in range(0,len(current_group)):
                tmp = current_group[i]
                if(tmp in order_dict.keys()):
                    length1 += 1

            for i in range(0,len(next_group)):
                tmp = next_group[i]
                if(tmp in order_dict.keys()):
                    length2 += 1

            if(length1 > 0):
                n = Fraction(1, length1)
            else:
                n = 0

            if(length2 > 0):
                m = Fraction(1, length2)
            else:
                m = 0


            for i in range(0,len(current_group)):
                tmp = current_group[i]
                if(tmp in order_dict.keys()):
                    order_dict[tmp] -= n

            for i in range(0,len(next_group)):
                tmp = next_group[i]
                if(tmp in order_dict.keys()):
                    order_dict[tmp] += m
        else:
            return








Test = Json_file()
Test.main()
