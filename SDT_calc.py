import argparse


class SDT:
    def __init__(self, indexer, data):

        self.calc_bucket = []
        self.total_docs = len(data)
        self.posting_list = indexer.posting_list

        self.productions = [('S', 'E !', None),  # 0
                            ('E', 'E | T', self.orOp),  # 1
                            ('E', 'T', None),  # 2
                            ('T', 'T ^ F', self.andOp),  # 3
                            ('T', 'F', None),  # 4
                            ('F', '( E )', None),  # 5
                            ('F', '~ F', self.notOp),  # 6
                            ('F', 'term', self.ins)]  # 7

        self.terminals = ['S', 'E', 'T', 'F']
        self.non_terminals = ['!', '|', '^', '~', '(', ')', 'term']

        self.all_symbols = self.terminals + self.non_terminals

        # Parse table optimized for code

        self.raw_parse_table = ['0 . . s4 . s5 s6 . . 1 2 3',
                                '1 s7 . . . . . acc',
                                '2 r2 s8 . r2 . . r2',
                                '3 r4 r4 . r4 . . r4',
                                '4 . . s4 . s5 s6 . . 9 2 3',
                                '5 . . s4 . s5 s6 . . . . 10',
                                '6 r7 r7 . r7 . . r7',
                                '7 . . s4 . s5 s6 . . . 11 3',
                                '8 . . s4 . s5 s6 . . . . 12',
                                '9 s7 . . s13 ',
                                '10 r6 r6 . r6 . . r6 ',
                                '11 r1 s8 . r1 . . r1 ',
                                '12 r3 r3 . r3 . . r3 ',
                                '13 r5 r5 . r5 . . r5']

        # ['0 . . s4 s5 . s6 . . 1 2 3',
        # '1 s7 . . . . . acc',
        # '2 r2 s8 . . r2 . r2',
        # '3 r4 r4 . . r4 . r4',
        # '4 . . . s5 . s6 . . . . 9',
        # '5 . . s4 s5 . s6 . . 10 2 3',
        # '6 r7 r7 . . r7 . r7',
        # '7 . . s4 s5 . s6 . . . 11 3',
        # '8 . . . s5 . s6 . . . . 12',
        # '9 r5 r5 . . r5 . r5',
        # '10 s7 . . . s13',
        # '11 r1 s8 . . r1 . r1',
        # '12 r3 r3 . . r3 . r3',
        # '13 r6 r6 . . r6 . r6']

        self.parse_table = [{'|': '', '^': '', '(': '', ')': '', '~': '', 'term': '', '!': '', 'S': '',
                             'E': '', 'T': '', 'F': ''} for i in range(len(self.raw_parse_table))]
        self.Initialize()

    def orOp(self):
        # print('Adding')
        if args.step_show:
            print(self.calc_bucket[-2], '|', self.calc_bucket[-1])
        res = set(self.calc_bucket[-2])
        for elem in self.calc_bucket[-1]:
            res.add(elem)
        self.calc_bucket[-2] = list(res)
        self.calc_bucket.pop()

    def notOp(self):
        # print('Uminusing')
        if args.step_show:
            print('~', self.calc_bucket[-1])
        res = [i for i in range(self.total_docs)
               if i not in self.calc_bucket[-1]]
        self.calc_bucket[-1] = res

    def andOp(self):
        # print('Multiplying')
        if args.step_show:
            print(self.calc_bucket[-2], '^', self.calc_bucket[-1])
        minList = self.calc_bucket[-1]
        otherList = self.calc_bucket[-2]
        if len(minList) > len(self.calc_bucket[-2]):
            minList = self.calc_bucket[-2]
            otherList = self.calc_bucket[-1]

        self.calc_bucket[-2] = [i for i in minList if i in otherList]
        self.calc_bucket.pop()

    def ins(self, x):
        # print('Inserting')
        self.calc_bucket.append(self.posting_list.get_Node_info(x)[1])

    # Productions with functions defined

    # S -> E
    # E -> E | T
    # E -> T
    # T -> T ^ F
    # T -> F
    # T -> ~ F
    # F -> ( E )
    # F -> id

    # raw_parse_table_orig = ['0 . s9 . s8 s7 . . . 6 5 4 3 2 1',
    #                    '1 r0 . . . . . . s21',
    #                    '2 r7 . . . . r7 r7 r7',
    #                    '3 r6 . . . . s20 r6 r6',
    #                    '4 r4 . . . . . r4 r4',
    #                    '5 r2 . . . . . s19 r2',
    #                    '6 acc',
    #                    '7 . s9 . s8 . . . . . . . . 18',
    #                    '8 . s17 . s16 s15 . . . . 14 13 12 11 10',
    #                    '9 r10 . . . . r10 r10 r10',
    #                    '10 . . s30 . . . . s29',
    #                    '11 . . r7 . . r7 r7 r7',
    #                    '12 . . r6 . . s28 r6 r6',
    #                    '13 . . r4 . . . r4 r4',
    #                    '14 . . r2 . . . s27 r2',
    #                    '15 . s17 . s16 . . . . . . . . 26',
    #                    '16 . s17 . s16 s15 . . . . 14 13 12 11 25',
    #                    '17 . . r10 . . r10 r10 r10',
    #                    '18 r8 . . . . r8 r8 r8',
    #                    '19 . s9 . s8 s7 . . . . . 24 3 2',
    #                    '20 . s9 . s8 s7 . . . . . 23 3 2',
    #                    '21 . s9 . s8 s7 . . . . 22 4 3 2',
    #                    '22 r1 . . . . . s19 r1',
    #                    '23 r5 . . . . . r5 r5',
    #                    '24 r3 . . . . . r3 r3',
    #                    '25 . . s34 . . . . s29',
    #                    '26 . . r8 . . r8 r8 r8',
    #                    '27 . s17 . s16 s15 . . . . . 33 12 11',
    #                    '28 . s17 . s16 s15 . . . . . 32 12 11',
    #                    '29 . s17 . s16 s15 . . . . 31 13 12 11',
    #                    '30 r9 . . . . r9 r9 r9',
    #                    '31 . . r1 . . . s27 r1',
    #                    '32 . . r5 . . . r5 r5',
    #                    '33 . . r3 . . . r3 r3',
    #                    '34 . . r9 . . r9 r9 r9']

    # Define Skeleton of Parse table

    # Makes the raw Parse table into machine friendly content

    def create_parse_table(self):
        parse_keys = list(self.parse_table[0].keys())
        for entry in self.raw_parse_table:
            x = entry.split(' ')
            ind = int(x[0])
            for i in range(1, len(x)):
                act = x[i]
                if act != '.':
                    self.parse_table[ind][parse_keys[i-1]] = act

    # Splits the raw string into usable tokens

    # def splitter(self, inp):
    #     inp += 'n'
    #     split_text = []
    #     pi = 0
    #     for i in range(len(inp)):
    #         ch = inp[i]
    #         if not ch.isdigit() and ch != '.':
    #             if pi != i:
    #                 split_text.append(inp[pi:i])
    #             split_text.append(ch)
    #             pi = i+1
    #         elif i == len(inp)-1:
    #             split_text.append(inp[pi:])

    #     return split_text

    # Apply bottom up parsing on the expression, and computes the result.

    def parser_text(self, split_text, DEBUG=True):
        self.Reset()
        stack_stage = [0]
        stack_inp = []
        while True:
            curr = split_text[0]
            curr_stage = stack_stage[-1]
            act = self.parse_table[curr_stage][curr if curr in self.all_symbols else 'term']
            if DEBUG:
                print(act)
            if act == 'acc':
                # Accept and return the result
                return self.calc_bucket[0]
            elif act == '':
                # Invalid Expression
                return "Error"
            else:
                if act[0].isdigit():
                    # GOTO
                    stack_stage.append(int(act))
                else:
                    if act[0] == 's':
                        # Shift
                        stack_inp.append(curr)
                        split_text.pop(0)
                        stack_stage.append(int(act[1:]))
                    elif act[0] == 'r':
                        # Reduce
                        work_prod = self.productions[int(act[1:])]
                        if work_prod[2] != None:
                            if work_prod[1] == 'term':
                                work_prod[2](stack_inp[-1])
                            else:
                                work_prod[2]()
                        for _ in work_prod[1].split(' '):
                            stack_stage.pop()
                            stack_inp.pop()
                        stack_inp.append(work_prod[0])
                        stack_stage.append(
                            int(self.parse_table[stack_stage[-1]][work_prod[0]]))
                        if DEBUG:
                            print(stack_stage[-1])

    # Initializer function

    def Initialize(self):
        self.create_parse_table()

    # Resetter function

    def Reset(self):
        self.calc_bucket.clear()

    # The function which calls all the other required functions

    def calc(self, inp):
        # print("Parsing : ", inp)
        # split_text = self.splitter(inp)
        # print(split_text)
        return self.parser_text(inp, args.debug)


# Command Line Argument Parser
# ----------------------------------------------------------------
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('true', 'True'):
        return True
    elif v.lower() in ('false', 'False'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


# Define flags for Debugging and Step showing
parser = argparse.ArgumentParser()
parser.add_argument('-db', '--debug', dest='debug',
                    default=False, help="Toggle Debug Info", choices=[True, False], type=str2bool)
parser.add_argument('-sth', '--step_show', dest='step_show',
                    default=False, help="Show Intermediate steps of Calculation", choices=[True, False], type=str2bool)

args = parser.parse_args()

# Input taker
# s = input()

# Call the calc function for finding the result of the expression
# calc(s)
