console = None

def init_console(_console):
    global console
    console = _console
    
    # arguments = name: str, function, is_multiple_args: bool, list_of_args: list, description: str plugin_name: str
    console.add_command('square', create_square, False, [float, float, str], 'square <width> <height> <char=\'@\'> - draws a square', __name__)

def create_square(width, height, char='@'):
    out = ''
    for y in range(int(height)):
        for x in range(int(width)):
            out += char
            if x == int(width)-1 and y != int(height)-1:
                out += '\n'
    return out