import os
import os.path
import sys

# Constants
ASM_FILE = 1
COMP_DICT = {'0': "110101010", '1': "110111111", "-1": "110111010",
             'D': "110001100",
             'A': "110110000", 'M': "111110000", "!D": "110001101",
             "!A": "110110001",
             "!M": "111110001", "-D": "110001111", "-A": "110110011",
             "-M": "111110011", "D+1": "110011111", "A+1": "110110111",
             "M+1": "111110111", "D-1": "110001110", "A-1": "110110010",
             "M-1": "111110010", "D+A": "110000010", "D+M": "111000010",
             "D-A": "110010011", "D-M": "111010011", "A-D": "110000111",
             "M-D": "111000111", "D&A": "110000000", "D&M": "111000000",
             "D|A": "110010101", "D|M": "111010101", "D>>": "010010000",
             "A>>": "010000000", "M>>": "011000000", "D<<": "010110000",
             "A<<": "010100000", "M<<": "011100000"}
DEST_DICT = {'M': "001", 'D': "010", 'A': "100", "MD": "011", "AM": "101",
             "AD": "110", "AMD": "111", "000": "000"}
JUMP_DICT = {'JGT': "001", 'JEQ': "010", 'JLT': "100", "JGE": "011",
             "JNE": "101", "JLE": "110", "JMP": "111", "000": "000"}


def populate_symbol_dict():
    """
    resets a dict it and fills it with the default symbols of hack.
    :return: the dict with all the default symbols pointing at the correct
        number for each one.
    """
    symbols = dict()
    symbols["SP"] = 0
    symbols["LCL"] = 1
    symbols["ARG"] = 2
    symbols["THIS"] = 3
    symbols["THAT"] = 4
    symbols["R0"] = 0
    symbols["R1"] = 1
    symbols["R2"] = 2
    symbols["R3"] = 3
    symbols["R4"] = 4
    symbols["R5"] = 5
    symbols["R6"] = 6
    symbols["R7"] = 7
    symbols["R8"] = 8
    symbols["R9"] = 9
    symbols["R10"] = 10
    symbols["R11"] = 11
    symbols["R12"] = 12
    symbols["R13"] = 13
    symbols["R14"] = 14
    symbols["R15"] = 15
    symbols["SCREEN"] = 16384
    symbols["KBD"] = 24576
    return symbols


def first_pass(symbols, lines):
    """
    goes over the lines in lines and if there are any jump declarations
    then it adds those as symbols to the symbols dict.
    :param symbols: a dict of symbols and their number.
    :param lines: a list of all the lines from the asm file.
    :return: the lines after the jumps were written to the symbols and the
        whitespaces were removed.
    """
    line_counter = 0
    # the lines without the jumps and whitespace
    new_lines = list()
    for line in lines:
        line = "".join(line.split())
        if "/" in line:
            line = line[0:line.index("/")]
        if len(line) == 0:
            continue
        if line[0] == "(":
            symbol = line[1:-1]
            symbols[symbol] = line_counter
        else:
            if line != "\n" and line[0] != "/":
                new_lines.append(line)
                line_counter += 1
    return new_lines


def read_file_in_args(file_name):
    """
    reads for the file given and stores each line in a list.
    :param file_name: the name of the file we read.
    :return: the list that stores the lines.
    """
    with open(file_name, "r") as file:
        lines = list()
        for line in file:
            lines.append(line)
    return lines


def go_over_lines(symbols, lines):
    """
    goes over each line of the asm file (again) and translates each line
    into the appropriate 16 bit representation.
    :param symbols: the dict with all the symbols in the file
        (minus variables).
    :param lines: a list where each cell is a line from the asm file.
    :return: a list where each cell is a 16 bit code representing the
        corresponding line in the asm file.
    """
    end_list = list()
    line_counter = 16
    for line in lines:
        bit_line = ""
        line_indicator = line[0]
        # if its an A instruction
        if line_indicator == '@':
            address = line[1::]
            # if it's a number then convert it to binary and add zeros
            # note: we assume the number isn't bigger then 16 bits
            if address.isdigit():
                bit_line = bin(int(address)).split('b')[1]
                while len(bit_line) < 16:
                    bit_line = '0' + bit_line
            # if it's a variable
            else:
                if address not in symbols:
                    symbols[address] = line_counter
                    line_counter += 1
                address_num = symbols[address]
                bit_line = bin(int(address_num)).split('b')[1]
                while len(bit_line) < 16:
                    bit_line = '0' + bit_line
        # its a C instruction
        else:
            bit_line += "1"
            # dividing the line to computation, destination and jump
            jump, dest = "000", "000"
            if '=' in line:
                dest, comp_jump = line.split('=')
                if ';' in comp_jump:
                    comp, jump = comp_jump.split(';')
                else:
                    comp = comp_jump
            else:
                comp, jump = line.split(';')
            bit_line += COMP_DICT[comp]
            bit_line += DEST_DICT[dest]
            bit_line += JUMP_DICT[jump]
        end_list.append(bit_line)
    return end_list


def main():
    list_of_files = list()
    # check if the path is a directory and fills list_of_files with all the
    # files names
    if os.path.isdir(sys.argv[ASM_FILE]):
        for filename in os.listdir(sys.argv[ASM_FILE]):
            if filename.endswith(".asm"):
                if sys.argv[ASM_FILE].endswith("/"):
                    list_of_files.append(
                        os.path.join(sys.argv[ASM_FILE] + "" + filename))
                else:
                    list_of_files.append(
                        os.path.join(sys.argv[ASM_FILE] + "/" + filename))
    else:
        list_of_files.append(sys.argv[ASM_FILE])
    # go over each file and deal with it as necessary
    for file_name in list_of_files:
        relative_file_name = file_name
        symbols = populate_symbol_dict()
        lines = read_file_in_args(relative_file_name)
        new_lines = first_pass(symbols, lines)
        bit_lines = go_over_lines(symbols, new_lines)
        write_file = file_name[0:-3] + "hack"
        with open(write_file, "w") as file:
            for line in bit_lines:
                file.write(line)
                file.write("\n")


if __name__ == '__main__':
    main()
