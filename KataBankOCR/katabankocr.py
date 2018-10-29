# KataBankOCR main module

# Expected length od the OCR line
expected_length=27

# List of check dictionaries where each element corresponds to a different line.
check_dict = [
    {
        "   ": (1, 4),
        " _ ": (0, 2, 3, 5, 6, 7, 8, 9),
    },
    {
        "| |": (0,),
        "  |": (1, 7),
        " _|": (2, 3,),
        "|_ ": (5, 6),
        "|_|": (4, 8, 9),
    },
    {
        "  |": (1, 4, 7),
        " _|": (3, 5, 9),
        "|_ ": (2,),
        "|_|": (0, 6, 8),
    }
]

def complement_with_spaces(line):
    """
    Complement the length of the line
    :param line: line with characters of OCR
    :return:
    """

    return line.ljust(expected_length)


def extract_each_letter_fragment(line, i):
    """
    Given a certain line of the ocr and the index of the letter, returns only the required characters
    :param line: string of OCR line
    :param i: position of the fragment
    :return: fragment correspondent to the i-th position
    """

    frag = line[(3 * i + 0):(3 * i + 3)]

    return frag


def check_possible_numbers(frag_list):
    """
    Receive the fragments and propose possible numbers
    :param frag_list: list with three fragments
    :return: list with three tuple of possible numbers
    """

    i=0
    n_list = []
    for value in frag_list:

        try:
            n = check_dict[i][value]
        except KeyError:
            n = 0

        n_list.append(n)
        i+=1

    return get_number_from_fragments(n_list)


def get_number_from_fragments(frag_list):
    """
    Estimates the number correspondent to the fragments
    :param frag_list: list of three line fragments
    :return: possible number for this fragment
    """

    n = "X"
    for i in (0,1,2,3,4,5,6,7,8,9):
        if i in frag_list[0] and i in frag_list[1] and i in frag_list[2]:
            n = str(i)
            break

    return n


def katabankocr(in0, in1, in2):
    """
    Kata Bank OCR module for the parse of the account number based on the output of the document paper scan
    :param in0: first line of the scan with 27 characters
    :param in1: second line of the scan with 27 characters
    :param in2: third line of the scan with 27 characters
    :return: number
    """

    in0 = complement_with_spaces(in0)
    in1 = complement_with_spaces(in1)
    in2 = complement_with_spaces(in2)

    number = ""
    for i in range(0,9):
        str0 = extract_each_letter_fragment(in0, i)
        str1 = extract_each_letter_fragment(in1, i)
        str2 = extract_each_letter_fragment(in2, i)
        n = check_possible_numbers([str0,str1,str2])
        number += n

    return number
