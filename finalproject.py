import sys
from math import *

# Global Array for the registers
#      s0 s1 s2 s3 s4 s5 s6 s7 t0 t1 t2 t3 t4 t5 t6 t7 t8 t9
reg = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
instruct = []
program_flow = []
stages = ["?", "IF", "ID", "EX", "MEM", "WB", "@"]
stages_taken = [False, False, False, False, False]
data = {}
cpucycles = 1
hazard_index = []
nop_indexes = []

"""

            TODO
            ----
            
* Confirm data hazard logic
  -------------------------
  If branches are in the previous 2 instructions are data hazards impossible since they are not writing? (guessing no but need validation)

* Possibly delete compare_instruct()
  ----------------------------------
  Confirm its unused/uneeded and delete   
  
* Forwarding
  ----------
  Probably just minor adjustments from non-forwarding (possibly done)
  Are there ONLY structural hazards? (ignoring control hazard present in cases where prediction is wrong) 
  
* TEST  
  ----
  Test edge cases wint lot of branches (perhaps numerous wrong branch predictions)
    - Validate program works properly when 2 nops are inserted (untested)  
    - Confirm beq works (minor probably works)
  Definitely longer programs with both failed/nonfailed branches  

"""

def branch_taken(index):
    """
    branch_taken operates when a branch is taken and performs all necessary operations to adjust all necessary data structures
    pre-conditions: a branch must be true in order for branch_taken to be called
    post-conditions: additional instructions added to program_flow
    :index: the desired line index where the branch instruction is located
    """
    if len(program_flow)-index-3>=0:
        remove = 4
    else:
        remove = len(program_flow)-index+1
    for counter in range(1,remove):
        #maybe
        # program_flow[index+counter].update_nop()
        stages_taken[stages.index(program_flow[index+counter].stage)-1] = False
        nop_indexes.append(index+counter)
    if index+3<=len(program_flow)-1:
        extra = index+4
        while index+3 != len(program_flow)-1:
            program_flow.pop(extra)
    function_name = program_flow[index].function_name
    just_copy = False
    for instruction in instruct:
        if (instruction.function_name == function_name) or just_copy:
            just_copy=True
            add_data(1)
            program_flow.append(Instruction(str(instruction.name) + " " + str(instruction.first_arg) + "," + str(instruction.second_arg) + "," + str(instruction.third_arg), str(function_name)))
            hazard_index.append(0)


def copy_data(last_moving_index, numOfLines):
    """
    copy_data duplicates rows when they must be moved down as a result of nops being inserted
    pre-conditions: a data hazard must occur with at least one nop being inserted
    post-conditions: the data dictionary is reformatted to properly display the current state
    :last_moving_index: the last index that is being "moved"
    :numOfLines: the number of lines that the rows are moving down
    :return: the current value of the register
    """
    lowest = len(program_flow)-1
    while lowest >= last_moving_index:
        for counter1 in range(1,17):
            data[lowest + numOfLines,counter1] = data[lowest, counter1]
        lowest-=1
    lowest+=2
    if numOfLines==2:
        for counter1 in range(1,17):
            data[lowest,counter1] = data[lowest-1, counter1]


def print_reg():
    """
    print_reg properly prints registers and their respective values
    post-conditions: registers are printed with each column with a fixed-width of 20 characters per column
    """
    global reg
    print()
    for counter in range(0,8):
        if (counter + 1) % 4 == 0:
            print("$s"+str(counter) + " = " + str(reg[counter]))
            continue
        print('{0: <20}'.format("$s"+str(counter) + " = " + str(reg[counter])), end="", flush=True)
    for counter in range(0,10):
        if (counter + 1) % 4 == 0 or counter is 9:
            print("$t" + str(counter) + " = " + str(reg[8 + counter]))
            continue
        print('{0: <20}'.format("$t"+str(counter) + " = " + str(reg[8+counter])), end="", flush=True)




def populate_nops():
    """
    populate_nops fills the data dictionary with the proper symbols for nops (and removes inactive nops)
    pre-conditions: at least one active nop needing to be printed in the nop_indexes list
    post-conditions: the correct key is given the "*" for the nop or nop is removed (when inactive)
    :return: the current value of the register
    """
    counter = 0
    while counter < len(nop_indexes):
        if nop_indexes[counter] is not 0:
            if cpucycles>5 and data[nop_indexes[counter], cpucycles-5]=="IF":
                nop_indexes.pop(counter)
                continue
            else:
                data[nop_indexes[counter], cpucycles]="*"
        counter+=1

def populate_data():
    """
    populate_data is the original function run to allocate the correct number of keys in the data dictionary
    post-conditions: data is structured to handle (at least the intial number) instructions
    """
    for row in range(0,len(program_flow)):
        for column in range(1, 17):
            data[row, column] = '.'

def add_data(numOfLines):
    """
    add_data is used to create additional keys in the data dictionary (when additional rows are needed for the program)
    pre-conditions: additional rows are required for the operation of the program
    post-conditions: the data dictionary is reformatted to properly run in the current state
    :numOfLines: the number of lines that are being added
    """
    for row in range(len(program_flow),numOfLines+len(program_flow)):
        for column in range(1, 17):
            data[row, column] = '.'

def print_data():
    """
    print_data prints the current state
    post-conditions: current state of instructions is printed per cpu cycle
    """
    print("CPU Cycles ===>     1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16")
    for row in range(0,len(program_flow)):
        break_early = True
        for column in range(1, 17):
            if data[row, column]!=".":
                break_early=False
                break
        if break_early:
            break
        program_flow[row].print_instruct()
        for column in range(1, 17):
            if column == 16:
                if data[row, column] == "@":
                    print(".", end="", flush=True)
                    continue
                else:
                    print(data[row, column], end="", flush=True)
                    continue
            if data[row,column]=="@":
                print('{0: <4}'.format(data[0, 16]), end="", flush=True)
            else:
                print('{0: <4}'.format(data[row, column]), end="", flush=True)
        print()

"""
# # # # # # # # # # # # # # # # # # # # # # # #
# Holds the Instruction data in a class       #
# Consists of different data including...     #
#   stage = 0,1,2,3,4 [IF,ID,EX,MEM,WB]       #
#   name = add, ori, or, addi etc.            #
#   function_name = loop, loop1, loop3 etc.   #
#       first_arg,second_arg,third_arg        #
#       isDone = holds if the instruction is done #
# # # # # # # # # # # # # # # # # # # # # # # #
"""


class Instruction(object):

    def __init__(self, I, function_name):
        self.stage = "?"
        self.function_name = function_name
        self.name, self.args = I.split()
        self.first_arg, self.second_arg, self.third_arg = self.args.split(",")

    def execute(self):
        """
        execute is the primary function used to control the function of the instruction
        post-conditions: the desired function of the instruction is performed
        :return: a function name if a branch is taken via bne/beq
        """
        if program_flow.index(self) in nop_indexes:
            return
        if (self.name == "ori") or (self.name == "or"):
            self.orr()
        elif (self.name == "add") or (self.name == "addi"):
            self.add()
        elif (self.name == "slt") or (self.name == "slti"):
            self.slt()
        elif (self.name == "beq"):
            return self.beq()
        elif (self.name == "bne"):
            return self.bne()
        elif (self.name == "and") or (self.name == "andi"):
            self.andd()

    def orr(self):
        """
        performs bitwise or operation
        post-conditions: bitwise operation performed and stored
        """
        reg_left = self.find_reg(self.second_arg)
        reg_right = self.find_reg(self.third_arg)
        reg_result = reg_left | reg_right
        self.place_reg(self.first_arg, reg_result)

    def add(self):
        """
        performs add operation
        post-conditions: add operation performed and stored
        """
        reg_left = self.find_reg(self.second_arg)
        reg_right = self.find_reg(self.third_arg)
        reg_result = reg_left + reg_right
        self.place_reg(self.first_arg, reg_result)

    def andd(self):
        """
        performs bitwise and operation
        post-conditions: bitwise and performed and stored
        """
        reg_left = self.find_reg(self.second_arg)
        reg_right = self.find_reg(self.third_arg)
        reg_result = reg_left & reg_right
        self.place_reg(self.first_arg, reg_result)

    def slt(self):
        """
        performs slt (determines whether arg2 is smaller than arg3
        post-conditions: slt operation performed and stored
        """
        reg_left = self.find_reg(self.second_arg)
        reg_right = self.find_reg(self.third_arg)
        if reg_left < reg_right:
            reg_result = 1
        else:
            reg_result = 0
        self.place_reg(self.first_arg, reg_result)

    def beq(self):
        """
        performs beq (branches if arg1 == arg2)
        post-conditions: branch operation performed if args equal or nothing otherwise
        """
        reg_left = self.find_reg(self.first_arg)
        reg_right = self.find_reg(self.second_arg)
        if (reg_left == reg_right):
            branch_taken(program_flow.index(self))

    def bne(self):
        """
        performs bne (branches if arg1 != arg2)
        post-conditions: branch operation performed if args not equal or nothing otherwise
        """
        reg_left = self.find_reg(self.first_arg)
        reg_right = self.find_reg(self.second_arg)
        if (reg_left != reg_right):
            branch_taken(program_flow.index(self))

    def place_reg(self, unparsed_string, val):
        """
        place_reg will find the register in the reg array and replace its value
        pre-conditions: a valid string/value is entered
        post-conditions: the desired register has its value updated
        :unparsed_string: unparsed_string is the desired register
        :val: the desired value for the register
        """
        global reg
        if(unparsed_string[1] == 't'):
            reg[int(unparsed_string[2]) + 8] = val
        else:
            reg[int(unparsed_string[2])] = val

    def find_reg(self, unparsed_string):
        """
        find_reg will find the register in the reg array and replace its value
        pre-conditions: a valid string/value is entered
        post-conditions: the desired register has its value updated
        :unparsed_string: unparsed_string is the desired register
        :val: the desired value for the register
        :return: the current value of the register
        """
        global reg
        if unparsed_string == "$zero":
            return 0
        elif str.isdigit(unparsed_string):
            return int(unparsed_string)
        elif(unparsed_string[1] == 't'):
            return reg[int(unparsed_string[2]) + 8]
        else:
            return reg[int(unparsed_string[2])]

    def compare_instruct(self,instruction):
        """
        compare_instruct compares two instructions (as a simple == would not be enough to compare two instruction objects)
        post-conditions: the equality of two instructions is returned
        :instruction: the second instruction that is being currently compared
        :return: True if the instructios are the same and False otherwise
        """
        if self.name == instruction.name and self.first_arg == instruction.first_arg and self.second_arg and instruction.second_arg and self.third_arg == instruction.third_arg:
            return True
        return False


    def print_instruct(self):
        """
        print_instruct is used to print the instruction in it's proper format
        post-conditions: the instruction (self) is printed before it's corresponding row
        """
        if self.first_arg == "nop":
            print('{0: <20}'.format(self.first_arg),end="", flush=True)
            return
        print('{0: <20}'.format(self.name + " " + self.first_arg + "," +  self.second_arg + "," + self.third_arg), end="", flush=True)

    def no_update(self):
        """
        no_update is run when an instruction is unable to update (as a result of a hazard and such)
        pre-conditions: the current instruction cannot update
        post-conditions: the instruction remains at the same stage for an additional cycle
        """
        if self.stage!= '?' and self.stage!= '@':
            data[program_flow.index(self), cpucycles] = self.stage

    def update_stage(self):
        """
        update_stage performs the necessary operations to data structures to properly push an update for an instruction
        pre-conditions: an instruction can be updated in the current cpucycle
        post-conditions: the instruction progresses to the next stage (if possible)
        """
        global stages
        if self.stage in stages and self.stage != "@":
            self.stage = stages[stages.index(self.stage) + 1]
            data[program_flow.index(self), cpucycles] = self.stage
            current_stage = stages.index(self.stage)
            if current_stage-1==5:
                stages_taken[4]=False
            elif current_stage==5:
                self.execute()
            if(current_stage-1)>=0 and (current_stage-1)<=4:
                stages_taken[current_stage-1]=True
                if (current_stage-1)>0:
                    stages_taken[current_stage-2]=False

    def can_update_stage(self):
        """
        can_update_stage checks if the next stage is being used by an instruction and returns the appropriate value
        post-conditions: Confirmation is returned on whether an update is possible
        :return: True if the next stage is unused and False otherwise
        """
        index = stages.index(self.stage)
        if index is 5:
            return True
        elif not stages_taken[index]:
            return True
        else:
            return False

def data_hazard(self, index):
    """
    data_hazard is used to detect data hazards between instructions
    post-conditions: the number of nops needed is returned
    :return 2 if two nops are required and 1 if one nop is required
    """
    global instruct
    if self.name=="bne" or self.name=="beq":
        compare_one = self.first_arg
        compare_two = self.second_arg
    else:
        compare_one = self.second_arg
        compare_two = self.third_arg
    if (1 <= stages.index(program_flow[index-1].stage) <= 5) and stages.index(program_flow[index].stage) == 2:
        if program_flow[program_flow.index(self)-1].first_arg == compare_one or program_flow[program_flow.index(self)-1].first_arg == compare_two:
            if program_flow[program_flow.index(self) - 1].name == "bne" or program_flow[program_flow.index(self) - 1].name == "beq":
                return False
            hazard_index.insert(index, 2)
            hazard_index.insert(index, 0)
            hazard_index.insert(index, 0)
            add_data(2)
            copy_data(index,2)
            program_flow.insert(index,Instruction("nop nop,nop,nop", "nop"))
            program_flow.insert(index,Instruction("nop nop,nop,nop", "nop"))
            nop_indexes.append(index)
            nop_indexes.append(index+1)
            return True
    if program_flow.index(self)>1:
        if (1 <= stages.index(program_flow[index - 2].stage) <= 5) and stages.index(program_flow[index].stage) == 2:
            if program_flow[program_flow.index(self) - 2].first_arg == compare_one or program_flow[program_flow.index(self) - 2].first_arg == compare_two:
                if program_flow[program_flow.index(self) - 2].name == "bne" or program_flow[program_flow.index(self) - 2].name == "beq":
                    return False
                hazard_index.insert(index, 1)
                hazard_index.insert(index, 0)
                add_data(1)
                copy_data(index, 1)
                nop_indexes.append(index)
                program_flow.insert(index,Instruction("nop nop,nop,nop", "nop"))
                return True
    hazard_index[index] = 0
    return False

def fill_data():
    """
    fill_data is used to populate the data dictionary (non-forwarding only)
    post-conditions: data is properly filled per cpu cycle
    """
    global program_flow
    index = 0
    while index < len(program_flow):
        if program_flow[index].stage == stages[6]:
            index+=1
            continue
        if index == 0:
            program_flow[0].update_stage()
            index+=1
            continue
        # print(program_flow[index].first_ar/g)
        if program_flow[index].first_arg == "nop":
            index += 1
            continue
        if hazard_index[index]==0:
            if data_hazard(program_flow[index], index):
                continue
        if program_flow[index].can_update_stage() and hazard_index[index]==0:
            program_flow[index].update_stage()
        else:
            if hazard_index[index] != 0:
                hazard_index[index]-=1
            program_flow[index].no_update()
        index+=1

def forward_fill_data():
    """
    forward_fill_data is used to populate the data dictionary (forwarding only)
    post-conditions: data is properly filled per cpu cycles
    """
    global program_flow
    index = 0
    while index < len(program_flow):
        if program_flow[index].stage == stages[6]:
            index+=1
            continue
        if index == 0:
            program_flow[0].update_stage()
            index+=1
            continue
        if program_flow[index].first_arg == "nop":
            index += 1
            continue
        if program_flow[index].can_update_stage():
            program_flow[index].update_stage()
        else:
            program_flow[index].no_update()
        index += 1

def non_forward_main():
    """
    non_forward_main is the main program logic when instructions are run without forwarding
    post-conditions: all necessary functions updated per cpucycle
    """
    global cpucycles
    while cpucycles in range(0,17):
        print("----------------------------------------------------------------------------------")
        fill_data()
        populate_nops()
        print_data()
        print_reg()
        cpucycles+=1
        if(program_flow[len(program_flow)-1].stage=="WB"):
            break

def forward_main():
    """
    forward_main is the main program logic when instructions are run with forwarding
    post-conditions: all necessary functions updated per cpucycle
    """
    global cpucycles
    while cpucycles in range(0,17):
        print("----------------------------------------------------------------------------------")
        forward_fill_data()
        populate_nops()
        print_data()
        print_reg()
        cpucycles+=1
        if (program_flow[len(program_flow) - 1].stage == "WB"):
            break

def main():
    """
    main is the entry point into the program and houses the logic to initialize the program
    """
    global hazard_index
    if len(sys.argv) != 3:
        sys.exit("Wrong number of arguments entered!")
    with open(sys.argv[2], 'r') as f:  # reading in the file line by line
        contents = f.readlines()
    # stripping \n from end of each line
    lines = [rec.rstrip('\n') for rec in contents]
    # finds the function name and initializes the class objects in the
    # instruct(instruction) array)
    function_name = "-"
    for line in contents:
        if ":" in line:
            function_name = line.rstrip(':')
            # line_number = contents.indexof(line)
            # functions.append((function_name, line_number))
        else:
            instruct.append(Instruction(line, function_name))
            program_flow.append(Instruction(line, function_name))
    populate_data()
    # Start of the Simulation
    print("START OF SIMULATION ", end="", flush=True)
    if sys.argv[1] == 'F':  # check to see if we need forwarding
        print("(forwarding)")
        forward_main()
    else:
        print("(no forwarding)")
        hazard_index = [0] * len(instruct)
        non_forward_main()
    print("----------------------------------------------------------------------------------")
    print("END OF SIMULATION")

if __name__ == '__main__':
    main()
