
def nextInSequence(number):
    if isinstance(number, int):
        if number % 2 == 0:
            return number // 2
        else:
            return 3*number+1
    else:
        raise TypeError('input must be int!')

def seqenceLength(number):
    length = 0
    while number != 1:
        number = nextInSequence(number)
        length += 1
    return length
