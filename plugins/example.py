NAME = 'example'

def init_console(add_command, console_variables):
    # arguments = name: str, function, is_multiple_args: bool, list_of_args: list, description: str
    add_command('square', create_square, False, [float, float, str], 'square <width> <height> <char> - draws a square')

def create_square(width: int, height: int, char: str):
    out = ''
    width = int(width)
    height = int(height)
    for y in range(height):
        for x in range(width):
            out += char
            if x == width-1 and y != height-1:
                out += '\n'
    return out