import random


# Nonogram solver (+GUI?)

class Row:
    # 0 none 1 filled 2 empty(unknown)

    def __init__(self, length, row_key=None, row_list=None):
        self.length = length
        self.row_value = [2 for index in range(length)]
        if row_key is None and row_list is None:
            self.fill_randomly()
        elif row_list is None:
            self.row_key = row_key
            self.row_list = Row.determine_row_list(row_key)
        elif row_key is None:
            self.row_list = row_list
            self.row_key = Row.reconstruct(length, row_list)
        else:
            self.row_key = row_key
            self.row_list = row_list

    def __str__(self):
        return str(self.row_value)

    def get_value(self):
        return self.row_value

    def get_key(self):
        return self.row_key

    def get_list(self):
        return self.row_list

    def set_value(self, value, position):
        """value will usually be either 0 or 1
        Position is indexed from 0 to self.length-1 inclusive
        Precondition: position is a valid index"""
        self.row_value[position] = value

    def set_value_list(self, value_list):
        self.row_value = value_list

    @staticmethod
    def determine_row_list(key):  #O(n)
        """Given a row_key, generates the corresponding row_list
        Precondition: key includes only 0s and 1s"""
        row_list = []
        temp_counter = 0
        for index in range(len(key)):
            if key[index] == 1:
                temp_counter += 1
            else:
                if temp_counter > 0:
                    row_list.append(temp_counter)
                temp_counter = 0
        if temp_counter > 0:
            row_list.append(temp_counter)
        return row_list

    @staticmethod
    def reconstruct(length, row_list):
        """Creates a random row key of the given length that
        is consistent with the given row_list
        Precondition: elements of row_list are positive integers
        Precondition: the length is not shorter than the min
        implementation of the row_list (with no gaps on the side
        and one 0 in between each stretch of 1s)
        Precondition: length>0"""
        add_pad_list = [0] * (len(row_list) + 1)
        for index in range(length - (sum(row_list) + len(row_list) - 1)):
            add_pad_list[random.randrange(len(row_list) + 1)] += 1
        return_list = [0] * add_pad_list[0]
        for index in range(len(row_list)):
            return_list = return_list + [1] * row_list[index] + \
                          [0] * (add_pad_list[index + 1] + 1)
        return_list.pop()
        # gets rid of the final 0 that is unnecessarily padded at the end
        return return_list

    @staticmethod
    def does_satisfy(row_value, expected_row_list):
        """Returns true iff the expected_row_list matches given row_value
        Precondition: row_value has been reduced to 0s and 1s"""
        if Row.determine_row_list(row_value) == expected_row_list:
            return True
        return False

    @staticmethod
    def generate_fillings_naive(row_value, row_list):
        """returns a list of all possible row_values
        with the required length (len(row_value)) and row_list
        Meant to be called recursively from the base call of
        Row.generate_fillings_naive(self.row_value,self.row_list)
        Returns [] if no valid arrangement satisfies
        Precondition: elements of row_list are positive integers"""
        if 2 not in row_value:  # case of fully determined guess
            if Row.does_satisfy(row_value, row_list):
                return [row_value]
            return []
        temp_zero = row_value[:]
        temp_one = row_value[:]
        first_two_index = row_value.index(2)
        temp_zero[first_two_index] = 0
        temp_one[first_two_index] = 1
        zero_fillings = Row.generate_fillings_naive(temp_zero, row_list)
        one_fillings = Row.generate_fillings_naive(temp_one, row_list)
        return zero_fillings + one_fillings

    @staticmethod
    def generate_fillings(row_value, row_list):
        """Equivalent to generate_fillings_naive, with the added goal
        of recursively shortening the space it looks at, so as to not
        cycle through the worst-case 2^len(row_value) variations
        Precondition: elements of row_list are positive integers"""
        if len(row_list) == 0:  # base case
            if 1 not in row_value:
                return [[0] * len(row_value)]
            else:
                return []
        # recursive case
        if sum(row_list) + len(row_list) - 1 > len(row_value):
            return []
        return_list = []
        first_val = row_list[0]
        temp_counter = 0
        counting_down = False
        count_down = first_val
        for index in range(len(row_value)):
            if row_value[index] == 1 or row_value[index] == 2:
                temp_counter += 1
            elif row_value[index] == 0:
                temp_counter = 0
            if row_value[index] == 1 or counting_down:
                counting_down = True
                count_down -= 1
            if count_down < 0:
                break
            if temp_counter >= first_val:
                first_part = [0] * (index + 1 - first_val) + [1] * first_val
                one_more = 0
                if index != len(row_value) - 1:
                    if row_value[index + 1] == 1:
                        continue
                    first_part = first_part + [0]
                    one_more = 1
                return_list = return_list + [first_part + filling for filling in
                                             Row.generate_fillings(row_value[index + 1 + one_more:], row_list[1:])]
        return [filling for filling in return_list if len(filling) == len(row_value)]

    @staticmethod
    def deduce(row_value, row_list):
        """Returns an updated row_value that retains all non-2 entries while
        replacing 2s with 0s or 1s iff those values are logically necessary
        for the row_value to have the potential of satisfying given row_list
        If the given row_value cannot possibly be filled to satisfy row_list, returns [-1]
        Precondition: elements of row_list must be positive integers. Hi"""
        fillings = Row.generate_fillings(row_value, row_list)
        num_fillings = len(fillings)
        if num_fillings == 0:
            return [-1]
        deduction = [2] * len(row_value)
        for index in range(len(row_value)):
            if row_value[index] != 2:
                deduction[index] = row_value[index]
                continue
            zero_counter = 0
            one_counter = 0
            for filling in fillings:
                if filling[index] == 0:
                    zero_counter += 1
                elif filling[index] == 1:
                    one_counter += 1
            if zero_counter == num_fillings:
                deduction[index] = 0
            elif one_counter == num_fillings:
                deduction[index] = 1
        return deduction

    def fill_randomly(self):
        self.row_key = [random.randrange(2) for index in range(self.length)]
        self.row_key[random.randrange(self.length)] = 1  # ensures at least one 1
        self.row_list = self.determine_row_list(self.row_key)

    def fill_randomly_enhanced(self):  # WIP
        max_clues = (self.length + self.length % 2) // 2
        num_clues = 1


class Grid:

    def __init__(self, xdim, ydim, key_array=None):
        """Precondition: xdim & ydim > 0
        Precondition: specified key_array must match dimensions
        (a ydim element-list, each element being an
        xdim-element list of 0s and 1s)"""
        self.xdim = xdim
        self.ydim = ydim
        if key_array is not None:
            self.xrows = [Row(xdim, row_key=key_array[row]) for row in range(ydim)]
        else:
            self.xrows = [Row(xdim) for row in range(ydim)]
        self.yrows = [Row(ydim, row_key=[self.xrows[inrow].get_key()[outrow]
                                         for inrow in range(ydim)]) for outrow in range(xdim)]
        self.x_row_lists = [self.xrows[index].get_list() for index in range(ydim)]
        self.y_row_lists = [self.yrows[index].get_list() for index in range(xdim)]

    def __str__(self):
        return_string = ""
        for index in range(self.ydim - 1):
            return_string += str(self.xrows[index]) + "\n"
        return_string += str(self.xrows[self.ydim - 1])
        return return_string

    def get_key_string(self):
        return_string = ""
        for index in range(self.ydim - 1):
            return_string += str(self.xrows[index].get_key()) + "\n"
        return_string += str(self.xrows[self.ydim - 1].get_key())
        return return_string

    def get_value_array(self):
        return [self.xrows[outer].get_value() for outer in range(self.ydim)]

    def update_value(self, hori_bool, new_value, row_index):
        """hori_bool=True denotes horizontal, False denotes vertical
        Precondition: If hori_bool, 0<=row_index<ydim and len(new_value)=xdim
        Precondition: If not hori_bool, 0<=row_index<xdim and len(new_value)=ydim"""
        if hori_bool:
            self.xrows[row_index].set_value_list(new_value)
            for index in range(self.xdim):
                self.yrows[index].set_value(new_value[index], row_index)
        else:
            self.yrows[row_index].set_value_list(new_value)
            for index in range(self.ydim):
                self.xrows[index].set_value(new_value[index], row_index)

    def is_solved(self):
        so_far_so = True
        for row in self.xrows:
            if row.get_key() != row.get_value():
                so_far_so = False
                break
        return so_far_so

    def naive_solve(self):
        """Uses Row.deduce and given row_lists to attempt to solve nonogram
        Will not guess or resolve ambiguity
        Will not use advanced solving techniques
        If it finds a solution, it will return a string of itself"""
        for cycle in range(300):
            if cycle % 2 == 0:
                for row_index in range(self.ydim):
                    self.update_value(True, Row.deduce(self.xrows[row_index].get_value(),
                                                       self.x_row_lists[row_index]), row_index)
            else:
                for column_index in range(self.xdim):
                    self.update_value(False, Row.deduce(self.yrows[column_index].get_value(),
                                                        self.y_row_lists[column_index]), column_index)
            if self.is_solved():
                return str(self)
            else:
                print(self)
                print()
        return "Can't solve it!"

    @staticmethod
    def solve(value_array, x_row_lists, y_row_lists, x_guess_index=0, y_guess_index=0):
        """Attempt to enumerate all solutions, or determine if no solutions are possible.
        Uses more advanced solving techniques: recursive guessing looking for contradictions
        Returns a list of all solution arrays"""
        solution_list = []
        starter = Grid.cap_guess(grid)
        for outer in range (len(value_array)):


    def num_solutions(self):
        # return len(Grid.solve(self))
        pass

    @staticmethod
    def cap_guess(value_array, x_row_lists, y_row_lists):
        """Uses a queue system to deduce and update using naive Row deductions and returns either
        a solved or semi-solved grid based on whether the deductions can be brought to completion
        The queue system also maximizes the information received from deductions, since Rows are only
        updated when new information from opposite direction Rows has been added to them
        If it finds an unresolvable contradiction, it will return [-1]
        Precondition: not an error array of [-1]"""
        x_queue = [i for i in range(len(value_array))]
        y_queue = [i for i in range(len(value_array[0]))]
        x_cycle = True  # if True, go through x_queue, and through y_queue if false
        max_dim = max(len(value_array), len(value_array[0]))
        while True:
            temp_hits = [0] * max_dim
            if x_cycle:
                for index in x_queue:
                    new_row = Row.deduce(value_array[index],x_row_lists[index])
                    if new_row == [-1]:
                        return [-1]
                    for
            if len(x_queue) == 0 or len(y_queue) == 0:
                break
            x_cycle = not x_cycle


"""
for attempt in range(10):
    temp_row = Row(12)
    temp_value = []
    for attempty in range(12):
        temp_param=random.uniform(0,1)
        if temp_param < .2:
            temp_insert = 0
        elif temp_param < .4:
            temp_insert = 1
        else:
            temp_insert = 2
        temp_value.append(temp_insert)
    print(temp_row.get_list())
    print(temp_value)
    print(Row.deduce(temp_value, temp_row.get_list()))
    print()

print(Row.deduce([2,2,0,0,2,2,2,2,2,2,2,0],[2,1,1,1]))
"""

myGrid = Grid(18, 24)

print(myGrid.get_key_string())
print()
print(myGrid.x_row_lists)
print(myGrid.y_row_lists)
print()
print(myGrid.naive_solve())
