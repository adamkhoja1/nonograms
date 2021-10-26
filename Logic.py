import random
import math

class Filling:
    """An immutable object representing what fills each square of a Nonogram

    Attributes -
    type - 0 is an X, 1 is a filled square, 2 is Empty,
           and 3 is the Error filling"""

    types = ['X','Filled','Empty','Error']
    comp_dict = {
                (0,0):0, (1,1):1, (2,2):2, (3,3):3,
                (0,2):0, (2,0):0, (1,2):1, (2,1):1,
                (0,1):3, (1,0):3, (0,3):3, (3,0):3,
                (1,3):3, (3,1):3, (2,3):3, (3,2):3
                }

    def __init__(self, type_index=2):
        assert type_index in [0,1,2,3], "Not a valid type assignment"
        self.type = type_index

    def __str__(self):
        return str(self.type)

    def __eq__(self, other):
        return self.type == other.get_type()

    def __ne__(self, other):
        return self.type != other.get_type()

    def get_type(self):
        return self.type

    def get_name(self):
        return Filling.types[self.type]

    def is_set(self):
        return self.type==0 or self.type==1

    def compare(self, other):
        return Filling(Filling.comp_dict[(self.type, other.get_type())])


class FillingArray():
    """
    A 2-d rectangular list of lists containing Fillings. Meant to be mutable.

    Attributes -
    numrows - number of rows in the array
    numcols - number of columns in the array
    array   - 2-d list of Fillings
    T       - another FillingArray instance that is the transpose of self
    """

    def __init__(self, numrows, numcols, type_array=None, gen_transpose=1):
        """Creates a filling array with the specificed columns. If no seed array is given,
        generates a random valid is_set Nonogram"""
        self.numrows = numrows
        self.numcols = numcols
        if type_array is not None:
            assert all([all([isinstance(element, int) for element in row]) \
                for row in type_array]), "type_array elements must be integers"
            self.array = [[Filling(filling_type) \
                for filling_type in row] for row in type_array]
        else: #Randomly fills with is_set fillings using Row methods
            self.array = self.generate_grid(numrows, numcols)
        self.T = None
        if gen_transpose:
            self.generate_transpose()

    def __str__(self):
        return_str = ""
        for row in self.array:
            return_str += str([filling.get_type() for filling in row])+"\n"
        return return_str[:-1]

    def get_dimensions(self):
        return (self.numrows, self.numcols)

    def get_filling(self, row, column):
        return self.array[row][column]

    def get_row(self, row_index):
        assert -self.numrows<=row_index<self.numrows
        return self.array[row_index]

    def get_col(self, column_index):
        assert -self.numcols<=column_index<self.numcols
        return self.T.array[column_index]

    def set_filling(self, type_or_filling, row, column):
        insertion = type_or_filling
        if isinstance(type_or_filling, int):
            insertion = Filling(type_or_filling)
        self.array[row][column] = insertion
        self.T.array[column][row] = insertion

    def set_row(self, row_or_filling_list, row_index):
        insertion = row_or_filling_list #Row or a list of Fillings
        if isinstance(row_or_filling_list, Row):
            insertion = row_or_filling_list.get_row_list()
        assert len(insertion) == self.numrows, "Wrong inserting row dimensions"
        assert isinstance(row_index, int) and -self.numrows<=row_index<self.numrows
        self.array[row_index] = insertion
        for column_index in range(len(insertion)):
            self.T.set_filling(insertion[column_index], column_index, row_index)

    def set_col(self, row_or_filling_list, col_index):
        self.array.T.set_row(row_or_filling_list, col_index)

    def deep_copy(self):
        type_array = [[self.array[row_index][column_index].get_type() \
            for column_index in range(self.numcols)] \
            for row_index in range(self.numrows)]
        return FillingArray(self.numcols, self.numrows, type_array)

    def generate_transpose(self):
        transpose_type_array = []
        for column_index in range(self.numcols):
            transpose_type_array.append([self.array[row_index][column_index].get_type() \
                for row_index in range(self.numrows)])
        transpose = FillingArray(self.numcols, self.numrows, transpose_type_array, 0)
        transpose.set_transpose(self)
        self.set_transpose(transpose)

    def set_transpose(self, transpose):
        assert self.numcols==transpose.numrows and self.numrows==transpose.numcols, "Wrong dimensions of transpose"
        self.T = transpose

    @staticmethod
    def generate_grid(numrows, numcols): #In the future, a density parameter could be added
        """
        Returns a randomly generated is_set 2d list of Fillings with the given dimensions
        Represents a valid Nonogram key
        """
        return_array = [Row(numcols).get_row_list() for _ in range(numrows)]
        for column in range(numcols):
            if not Row.determine_fill_list([return_array[row][column] for row in range(numrows)]):
                temp_row = random.randrange(numrows)
                return_array[temp_row][column] = Filling(1)
        return return_array

    @staticmethod
    def is_set(filling_array_or_row_or_row_list):
        short = filling_array_or_row_or_row_list
        if isinstance(short, FillingArray): #Rows are included, as a subclass
            for row in short.array:
                for filling in row:
                    if not filling.is_set():
                        return False
            return True
        #Otherwise we are dealing with a row_list
        return all([i.is_set for i in short])

    @staticmethod
    def has_errors(filling_array_or_row_or_row_list):
        short = filling_array_or_row_or_row_list
        if isinstance(short, FillingArray): #Rows are included, as a subclass
            for row in short:
                for filling in row:
                    if filling.get_type() == 3:
                        return True
            return False
        #Otherwise we are dealing with a row_list
        return any([i.get_type() == 3 for i in short])

class Row(FillingArray):
    """Type of FillingArray with only one row; still a 2-d list containing the FillingList"""

    def __init__(self, length, row_type_list=None):
        self.numrows = 1
        self.numcols = length
        if row_type_list is not None:
            self.array = [[Filling(f) for f in row_type_list]]
        else: #Randomly fills with is_set fillings using Row methods
            self.fill_randomly()

    def get_row_list(self):
        return self.array[0]

    def get_filling(self, index):
        return self.array[0][index]

    def set_filling(self, type_or_filling, index):
        insertion = type_or_filling
        if isinstance(type_or_filling, int):
            insertion = Filling(type_or_filling)
        self.array[0][index] = insertion

    def set_row(self, row_or_filling_list, row_index):
        assert False, "Rows cannot have their entire contents reset"

    def generate_transpose(self):
        assert False, "Rows do not support transposes"

    def set_transpose(self, transpose):
        assert False, "Rows do not support transposes"

    def fill_randomly(self): #In the future, a density parameter could be added
        self.array = [[Filling(random.randrange(2)) for _ in range(self.numcols)]]
        self.set_filling(1, random.randrange(self.numcols)) # ensures at least one fill

    @staticmethod
    def compare_rows(r1, r2):
        """
        Outputs a list of fillings, of elementwise comparisons between
        the two input fillings at each index
        r1 and r2 can be either Rows or lists of Fillings
        Must be of equal length in either case
        """
        temp1, temp2 = r1, r2
        if isinstance(r1, Row):
            temp1 = r1.get_row_list()
        if isinstance(r2, Row):
            temp2 = r2.get_row_list()
        assert len(temp1) == len(temp2), "Compared rows must be the same size"
        return [Filling.compare(temp1[i], temp2[i]) for i in range(len(temp1))]

    @staticmethod
    def determine_fill_list(row_or_filling_list): #O(n)
        """Given an is_set Row or list of fillings, generates the corresponding fill_list"""
        row_list = row_or_filling_list
        if isinstance(row_or_filling_list, Row):
            row_list = row_or_filling_list.get_row_list()
        assert Row.is_set(row_list), "Not a set filling"
        fill_list = []
        temp_counter = 0
        for index in range(len(row_list)):
            if row_list[index].get_type() == 1:
                temp_counter += 1
            else:
                if temp_counter:
                    fill_list.append(temp_counter)
                temp_counter = 0
        if temp_counter:
            fill_list.append(temp_counter)
        return fill_list

    @staticmethod
    def reconstruct(length, fill_list):
        """Creates a random Row of the given length that is consistent with the given fill_list"""
        num_gaps = len(fill_list) + 1
        add_pad_list = [0] * (num_gaps)
        assert length - (sum(fill_list) + num_gaps - 2) >= 0, \
            "Not enough space to construct minimal filling_list"
        # The expression (sum(fill_list) + num_gaps - 2) is the minimum size of
        # any row with the given fill_list. The difference between length and this
        # Minimum is thus the number of buffer X's we can place throughout
        for index in range(length - (sum(fill_list) + num_gaps - 2)):
            add_pad_list[random.randrange(num_gaps)] += 1
        return_list = [Filling(0)] * add_pad_list[0]
        for index in range(len(fill_list)):
            return_list = return_list + [Filling(1)] * fill_list[index] + \
                          [Filling(0)] * (add_pad_list[index + 1] + 1)
        return return_list[:-1]

    @staticmethod
    def does_satisfy(pub_row, expected_fill_list):
        """Returns whether the expected_row_list matches given pub_row"""
        return Row.is_set(pub_row) and Row.determine_fill_list(pub_row) == expected_fill_list

    @staticmethod
    def generate_candidates(pub_row, fill_list):
        """
        pub_row is a list of fillings (usually not is_set)
        Recursively produces a list of all possible row_lists with the required
        length (len(pub_row)) and fill_list, and such that any is_set fillings
        in pub_row are retained
        Returns [] if no valid arrangement satisfies
        """
        #assert not Row.has_errors(pub_row)
        if not len(fill_list):  # base case
            if any([filling.get_type()==1 for filling in pub_row]):
                return []
            else:
                return [[Filling(0)] * len(pub_row)]
        # recursive case
        if sum(fill_list) + len(fill_list) - 1 > len(pub_row):
            return []
        return_list = []
        first_val = fill_list[0]
        temp_counter = 0
        counting_down = False
        count_down = first_val
        for index in range(len(pub_row)):
            if pub_row[index].get_type() == 1 or pub_row[index].get_type() == 2:
                temp_counter += 1
            elif pub_row[index].get_type() == 0:
                temp_counter = 0
            if pub_row[index].get_type() == 1 or counting_down:
                counting_down = True
                count_down -= 1
            if count_down < 0:
                break
            if temp_counter >= first_val:
                first_part = [Filling(0)] * (index + 1 - first_val) + \
                    [Filling(1)] * first_val
                one_more = 0
                if index != len(pub_row) - 1:
                    if pub_row[index + 1].get_type() == 1:
                        continue
                    first_part = first_part + [Filling(0)]
                    one_more = 1
                return_list = return_list + [first_part + candidate for candidate in
                    Row.generate_candidates(pub_row[index + 1 + one_more:], fill_list[1:])]
        return [candidate for candidate in return_list if len(candidate) == len(pub_row)]

    @staticmethod
    def deduce(pub_row, fill_list):
        """
        Returns a 2-tuple: first val is an updated pub_row that retains all is_set entries while
        replacing empty fillings with fills or x's iff those values are logically necessary
        for the pub_row to have the potential of satisfying given fill_list.
        The second value of the return tuple is a boolean representing whether the deduction is
        impossible, i.e. that the given pub_row cannot possibly be filled to satisfy fill_list

        Arguments:
        pub_row - A row list
        """
        #assert all([e>0 for e in fill_list]), "Elements of fill_list must be positive integers"
        #assert not Row.has_errors(pub_row), "An error was already present in given pub_row"
        candidates = Row.generate_candidates(pub_row, fill_list)
        if len(candidates) == 0:
            return pub_row, 1
        deduction = [Filling()] * len(pub_row)
        for candidate in candidates:
            deduction = Row.compare_rows(deduction, candidate)
        for column_index in range(len(deduction)):
            if deduction[column_index].get_type()==3:
                deduction[column_index] = Filling() #Errors only represent ambiguity; the preassumption is that there are
                # No preexisting errors, and if a given pub_row is intractible, we expect generate_candidates
                # To catch this through producing an empty candidates list, so error fillings are replaced
                # With empty fillings
        return deduction, 0

class Grid:
    """
    Represents a Nonogram Grid

    Attributes:
    numrows        - Number of rows in the Grid
    numcols        - Size of each row in the list
    key_array      - is_set FillingArray representing key of Grid
    pub_array      - FillingArray representing pub_rows of Grid
    row_fill_lists - numrows-length list of fill_lists
    col_fill_lists - numcols-length list of fill_lists
    cycle_list     - list of ints representing each row and column in a special order
                     useful for solving. See construct_cycle_list method for details
    """

    def __init__(self, numrows, numcols, key_array=None):
        """
        Constructs a Grid with the given dimensions. If a key_array is provided,
        set the Grid's key_array to it, else generate a random valid Nonogram key

        Precondition: specified key_array must match dimensions
        key_array is an is_set FillingArray
        (a numrows element-list, each element being an
        numcols-element list of is_set Fillings)"""
        assert isinstance(numcols, int) and isinstance(numrows, int), \
            "Dimensions must be integers"
        assert numrows >= 0 and numcols >= 0, "Dimensions must be positive"
        self.numcols = numcols
        self.numrows = numrows
        if key_array is not None:
            assert isinstance(key_array, FillingArray), \
                "Given key_array must be a FillingArray"
            assert key_array.get_dimensions() == (numrows, numcols), \
                "Given key_array's dimensions do not match expected dimensions"
            assert FillingArray.is_set(key_array), "Given key_array is not is_set"
            self.key_array = key_array
        else:
            self.key_array = FillingArray(numrows, numcols)
        self.pub_array = FillingArray(numrows, numcols, \
            [[2 for column in range(numcols)] for row in range(numrows)])
        self.row_fill_lists = [Row.determine_fill_list(self.key_array.get_row(row_index)) \
            for row_index in range(numrows)]
        self.col_fill_lists = [Row.determine_fill_list(self.key_array.get_col(column_index)) \
            for column_index in range(numcols)]
        self.cycle_list = self.construct_cycle_list(numrows, numcols)

    def __str__(self):
        return str(self.pub_array)

    def get_key_str(self):
        return str(self.key_array)

    def get_pub_array(self):
        return self.pub_array

    def get_key_array(self):
        return self.key_array

    def self_solve(self):
        return Grid.solve(self.pub_array, self.row_fill_lists, \
            self.col_fill_lists, self.cycle_list)

    def is_solved(self):
        return self.pub_array == self.key_array

    @staticmethod
    def is_solved(pub_array, row_fill_lists, col_fill_lists):
        for row_index in range(pub_array.numrows):
            if not Row.does_satisfy(pub_array.get_row(row_index), row_fill_lists[row_index]):
                return False
        for column_index in range(pub_array.numcols):
            if not Row.does_satisfy(pub_array.get_col(column_index), \
                col_fill_lists[column_index]):
                return False
        return True

    @staticmethod
    def construct_cycle_list(numrows, numcols):
        cycle_list = []
        max_dim = max(numrows, numcols)
        min_dim = min(numrows, numcols)
        row_cycle_list = [math.ceil(index/2) if index%2 else -math.ceil(index/2) \
            for index in range(numrows)]
        col_cycle_list = [2*max_dim + math.ceil(index/2) if index%2 \
            else 2*max_dim - math.ceil(index/2) \
            for index in range(numcols)]
        #Merge
        for _ in range(min_dim):
            cycle_list.append(row_cycle_list.pop(0))
            cycle_list.append(col_cycle_list.pop(0))
        if row_cycle_list:
            cycle_list.extend(row_cycle_list)
        else:
            cycle_list.extend(col_cycle_list)
        return cycle_list

    @staticmethod
    def solve(pub_array, row_fill_lists, col_fill_lists, cycle_list):
        """Attempt to enumerate all solutions, or determine if no solutions are possible.
        Uses recursive guessing, looking for contradictions
        Does not mutate input FillingArray pub_array
        Returns a list of all solution arrays"""
        starter, error = Grid.cap_guess(pub_array, row_fill_lists, col_fill_lists)
        if error:
            return []
        elif Grid.is_solved(starter, row_fill_lists, col_fill_lists):
            return [starter]
        ####Mistake in this method: likely with the way cycle_list is passed###
        def probe(hori_bool, index, cycle_index):
            sub_solutions = []
            if hori_bool:
                array = starter
                fill_list = row_fill_lists[index]
            else:
                array = starter.T
                fill_list = col_fill_lists[index]
            for candidate in Row.generate_candidates(array, fill_list):
                temp = array.deep_copy()
                temp.set_row(candidate, cycle)
                sub_solutions.extend(Grid.solve(temp, row_fill_lists, \
                    col_fill_lists, cycle_list[cycle_index+1:]))
        solution_list = []
        #Probe each (not is_set) row/col in cycle order
        max_dim = max(pub_array.numrows, pub_array.numcols)
        for outer in range(len(cycle_list)):
            cycle = cycle_list[outer]
            hori_bool = cycle < max_dim
            if not hori_bool:
                cycle -= 2*max_dim
            if (hori_bool and Row.is_set(pub_array.get_row(cycle))) or \
                (not hori_bool and Row.is_set(pub_array.get_col(cycle))):
                continue
            solution_list.extend(probe(hori_bool, cycle, outer))
        return solution_list

    @staticmethod
    def cap_guess(pub_array, row_fill_lists, col_fill_lists):
        """
        Returns a 2-tuple. First element is an updated (or solved) pub_array using the fill_lists
        Second element is an error boolean, 1 if there was an intractibility between the input
        pub_array and the fill_lists

        Does not mutate input FillingArray

        Uses a queue system to deduce and update using naive Row deductions and returns either
        a solved or semi-solved grid based on whether the deductions can be brought to completion
        The queue system also maximizes the information received from deductions, since Rows are only
        updated when new information from opposite direction Rows has been added to them

        Arguments:
        pub_array      - FilingArray representing public array
        row_fill_lists - list of lists; row_fillings for each row
        col_fill_lists - list of lists; col_fillings for each col
        Precondition: correct dimensions
        """
        if FillingArray.is_set(pub_array):
            return pub_array, not Grid.is_solved(pub_array, row_fill_lists, col_fill_lists)
        return_array = pub_array.deep_copy()
        row_cycle = 1  # if True, go through row_queue, and through col_queue if false
        queue = set(range(pub_array.numrows)) #row_queue to begin with
        other_queue = set(range(pub_array.numcols)) #col_queue to begin with
        while len(queue):
            if row_cycle:
                temp_array = return_array
                fill_lists = row_fill_lists
            else:
                temp_array = return_array.T
                fill_lists = col_fill_lists
            for index in queue:
                temp_row, temp_error = Row.deduce(temp_array.get_row(index), \
                    fill_lists[index])
                if temp_error:
                    return return_array, 1
                differences = set(filter(lambda i: temp_array.get_filling(index, i) != temp_row[i], range(temp_array.numcols)))
                other_queue = other_queue.union(differences)
                temp_array.set_row(temp_row, index)
            row_cycle = not row_cycle
            queue, other_queue = other_queue, queue
            other_queue = set()
        return return_array, 0

test_key_array = FillingArray(13, 13, [
[1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0],
[1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1],
[1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1],
[1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
[1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1],
[1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0],
[0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0],
[1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1],
[0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0],
[1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
[1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
[1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1]
])
test = Grid(13, 13, test_key_array)
print(test.get_key_str())
print()
#print(test.row_fill_lists)
#print(test.col_fill_lists)
#print()
print(Grid.cap_guess(test.pub_array, test.row_fill_lists, test.col_fill_lists)[0])
print()
print(len(test.self_solve()))