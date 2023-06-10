#!/usr/bin/python3
########################################################################################################################
# Simple tool to calculate expenses in hierarchically-organized categories.
# Expenses are stored in a file with the following structure:
#
# Category 1            0
#   Category 1.1        0
#     Expense 1         100
#     Expense 2         200
#   Category 1.2        0
#     Expense 3         300
#
# Tree structure is formed by indentation with spaces.
# Expense amount is separated with one ore more TABs.
#
# Usage:
# 1. Add the expense to the appropriate category
# 2. Run the tool to recalculate expenses. Expenses within categories will be summed and updated as necessary
#
# The contents of the file becomes:
#
# Category 1            600
#   Category 1.1        300
#     Expense 1         100
#     Expense 2         200
#   Category 1.2        300
#     Expense 3         300
#
########################################################################################################################
import re
import sys
from dataclasses import dataclass
from typing import List, IO

TAB_SIZE = 8


@dataclass
class ExpensesNode:
    indent: int
    key: str
    value: float
    items: List['ExpensesNode']

    def calculate_value(self):
        if len(self.items) > 0:
            self.value = sum((item.calculate_value() for item in self.items))
        return self.value

    def max_indent_and_key_length(self):
        items_max = max((item.max_indent_and_key_length() for item in self.items)) if len(self.items) > 0 else 0
        return max(self.indent + len(self.key), items_max)


class ExpensesTreeReader:
    file_name: str

    def __init__(self, file_name: str):
        self.file_name = file_name

    @staticmethod
    def indent_of(s: str):
        indent = 0
        for c in s:
            if c != ' ':
                return indent
            indent += 1

    def read(self):
        with open(self.file_name) as file:
            root = ExpensesNode(-1, '', 0, [])
            stack = [root]

            while line := file.readline().rstrip():
                parts = re.split('\t+', line)
                if len(parts) != 2:
                    raise ValueError(parts)
                cur_indent = ExpensesTreeReader.indent_of(parts[0])
                node = ExpensesNode(cur_indent, parts[0][cur_indent:], float(parts[1]), [])
                prev_indent = stack[-1].indent

                if cur_indent > prev_indent:
                    parent = stack[-1]
                    parent.items.append(node)
                    stack.append(node)
                elif cur_indent < prev_indent:
                    while stack[-1].indent >= cur_indent:
                        stack.pop()
                    parent = stack[-1]
                    parent.items.append(node)
                    stack.append(node)
                else:
                    parent = stack[-2]
                    parent.items.append(node)
                    stack.pop()
                    stack.append(node)

            if len(root.items) > 1:
                raise ValueError('There must be only 1 root node')
            return root.items[0]


class ExpensesTreeWriter:
    file: IO

    def __init__(self, file: IO):
        self.file = file

    def write(self, root: ExpensesNode):
        key_area_size = (root.max_indent_and_key_length() + TAB_SIZE) // TAB_SIZE * TAB_SIZE
        self.__write(root, key_area_size)

    def __write(self, node: ExpensesNode, key_area_size: int):
        key_area_chars = ' ' * node.indent + node.key
        n_tabs = (key_area_size - len(key_area_chars) + TAB_SIZE - 1) // TAB_SIZE
        self.file.write(key_area_chars + '\t' * n_tabs + f'{node.value:g}\n')
        for item in node.items:
            self.__write(item, key_area_size)


def recalculate(file_name, output_file_name):
    expenses = ExpensesTreeReader(file_name).read()
    expenses.calculate_value()

    if output_file_name == '-':
        ExpensesTreeWriter(sys.stdout).write(expenses)
    else:
        with open(output_file_name, 'w') as file:
            ExpensesTreeWriter(file).write(expenses)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: expenses.py <recalc> <file> [output file name or '-' for stdout]", file=sys.stderr)
        sys.exit(1)

    recalculate(sys.argv[2], sys.argv[2] if len(sys.argv) == 3 else sys.argv[3])
