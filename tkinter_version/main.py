from importlib import import_module
from threading import Thread
from time import sleep
import os
import sys

NAME = 'SuadoScript'
VERSION = '0.1.0' # beta (that was super fast)

def check_type(string: str, type):
    if type == float:
        try:
            float(string)
            return True
        except ValueError:
            return False
    if type == str:
        return True
    return False

def convert_path(path: str, convert_to: str=os.path.sep, separators: list=['\\','/']):
    for i in separators:
        path = path.replace(i, convert_to)
    return path

class IncrementVariable:
    def __init__(self, value: float, minvalue: float, maxvalue: float, delta: float):
        self.value = float(value)
        self.minvalue = float(minvalue)
        self.maxvalue = float(maxvalue)
        self.delta = float(delta)

    def increment(self):
        if self.value >= self.maxvalue:
            self.value = self.minvalue
        elif self.value < self.minvalue:
            self.value = self.minvalue
        else:
            self.value += self.delta

        return self.value

    def get_value(self):
        return self.value

class Console:
    def __init__(self, separator: str=';', cfg_path: str='./cfg', plugins_path: str='plugins', use_default_commands: bool=True):
        #self.historic = []
        #self.commandhistoricline = 0
        #self.tab_selected = 0

        self.colors = {
            'output':{
                'error': (255,0,0),
                'default': (255,255,255)
            }
        }

        self.cfg_path = convert_path(cfg_path)
        self.cfg_configfile = 'config.cfg'
        
        self.plugins_path = convert_path(plugins_path)
        self.plugins = {}

        self.separator = separator
        self.alias_separator = '&&'
        self.return_char = '@'
        self.plus_char = '+'
        self.minus_char = '-'

        self.aliases = {}
        self.loop_aliases = {}
        self.loop_aliases_on = []

        self.threads = []

        self.incrementvariables = {}

        self.running_commands = []
        self.ignore_commands = []
        self.toggle_commands = []

        if use_default_commands:
            self.valid_commands = {
                # command_name(str) : [function(FunctionType), is_multiple_args(bool), list_of_args_needed(list), description(str)]
                "quit": [self.quit,False, [], "quit - ends the console loop."],
                "commands": [self.get_commands,False, [], "commands - Show a list of commands."],
                "help": [self._help,False, [str], "help <command> - Shows the description of the specified command."],
                "echo": [self.echo,True, [str], "echo <args> - Prints out to the console what is inside of the parameter <args>."],
                "exec": [self.exec_cfg,False, [str], "exec <file_path> - Executes the specified file interpreting it as a cfg."],
                #"clear": [self.clear,False, [], "clear - clears the console output screen."],
                "alias": [self.alias,True, [str], "alias <alias_name> <commands> - Creates an alias command, called the same as the parameter <alias_name> content, with the <commands> parameter as his function."],
                "loop_alias": [self.loop_alias,True, [str], "loop_alias <alias_name> <commands> - Creates an loop_alias command that when called, toggles from executing commands and stop executing commands."],
                #"bind": [bind,True, [str], "bind <key> <commands> - Binds the specified key with the specified commands, so when the key is pressed, invokes all of the commands."], # pygame and tkinter
                #"unbind": [unbind,False, [str], "unbind <key> - Erases the keybind."], # pygame and tkinter
                "incrementvar": [self.create_incrementvar,False, [float, str, float, float, float], "incrementvar <value> <var_name> <minvalue> <maxvalue> <delta> - Creates an instance of incrementvar class wich can be incremented by invoking the incrementvar name and getting the output using " + self.return_char + "<var_name>."],
                #"toggleconsole": ["toggleconsole",False, [], None], # pygame
                #"togglemenu": ["togglemenu",False, [], None], # pygame
                "aliases": [self.get_aliases,False,[], "aliases - Show a list of aliases."],
                "plugin_load": [self.plugin_load, False, [str], "plugin_load <file_path> - Loads a python script."],
                "plugin_unload": [self.plugin_unload, False, [str], "plugin_unload <plugin_name> - Removes the plugin commands."],
                "wait": [self.wait, False, [float], "wait <seconds> - Stops the line execution for the specified time in seconds."]
            }
        else:
            self.valid_commands = {}
        
        self.exec_cfg(self.cfg_configfile)

    def wait(self, seconds: float):
        sleep(float(seconds))

    def plugin_load(self, file_path: str):
        if not file_path.endswith('.py'):
            file_path += '.py'
        
        if not os.path.exists(file_path):
            file_path = os.path.join(self.plugins_path, os.path.basename(file_path))
            if not os.path.exists(file_path):
                return ['File does not exists.', self.colors['output']['error']]

        file_path = convert_path(file_path.replace('.py',''), '.')

        plugin = import_module(file_path)
        plugin_name = plugin.NAME
        if plugin_name not in self.plugins:
            self.plugins[plugin_name] = []

            def plugin_add_command(name: str, *args, **kwargs):
                self.add_command(name, *args, **kwargs)
                self.plugins[plugin_name].append(name)
            try:
                plugin_output = plugin.init_console(plugin_add_command, {
                    'colors':self.colors, # should i just let the plugin add/modify/remove colors or should i just copy the dict?
                    'separator':self.separator,
                    'incrementvariable':IncrementVariable,
                    'check_type':check_type,
                    'convert_path':convert_path,
                    'cfg_path':self.cfg_path,
                    'cfg_configfile':self.cfg_configfile,
                    'alias_separator':self.alias_separator,
                    'return_char':self.return_char,
                    'plus_char':self.plus_char,
                    'minus_char':self.minus_char
                })
            except:
                return [f'Could not initialize plugin \"{plugin_name}\"', self.colors['output']['error']]
            
            return plugin_output
        else:
            return ['Plugin is already loaded.', self.colors['output']['error']]

    def plugin_unload(self, plugin: str):
        if plugin not in self.plugins:
            return [f'{plugin} is not loaded.', self.colors['output']['error']]
        
        for c in self.plugins[plugin]:
            if c in self.valid_commands:
                for i in c:
                    if i != None:
                        del(i)
                self.valid_commands.pop(c)
        
        self.plugins.pop(plugin)

    def add_command(self, name: str, function, is_multiple_args: bool, list_of_args: list, description: str):
        self.valid_commands[name] = [function, is_multiple_args, list_of_args, description]

    def handle_input(self, text):
        words = text.strip().split()

        if len(words) == 0:
            return
        
        command_word = words[0]
        words.pop(0)
        if command_word in self.valid_commands:
            c = self.valid_commands[command_word]
            if c[1] == False: # is_multiple_args check
                if len(words) != len(c[2]): # da erro se estiver faltando argumentos ou tiver muitos argumentos
                    return ['Failure executing command "' + command_word + '" expected ' + str(len(c[2])) + ' parameters', self.colors['output']['error']]
            
            checktype = None
            for i in range(len(words)):
                if command_word in self.valid_commands:
                    pass
                else:
                    if words[i].startswith(self.return_char):
                        for cc in self.incrementvariables.copy():
                            if words[i] == self.return_char + cc:
                                words[i] = str(self.incrementvariables[cc].get_value())
                    
                if c[1] == True:
                    checktype = check_type(words[i], c[2][0])
                else:
                    checktype = check_type(words[i], c[2][i])
                    
                if not checktype:
                    return ['Failure executing command "' + command_word + '" parameter ' + str(i+1) + ' "' + words[i] + '" is the wrong type', self.colors['output']['error']]
                
            if c[1] == True:
                words = [words]
            
            self.set_running_command(command_word)
            return c[0](*words)
        
        if len(words) == 0: # se for só command_word ou seja n tem arg
            if command_word in self.aliases: # se loop de alias funciona, por que de alias nao?
                if command_word.startswith(self.plus_char) and len(command_word) != len(self.plus_char):
                    temp = command_word
                    for i in range(len(self.plus_char)):
                        temp[i] = ''
                    
                    if temp in self.toggle_commands:
                        pass
                    else:
                        self.toggle_commands.append(temp)
                        temp = None
                elif command_word.startswith(self.minus_char) and len(command_word) != len(self.minus_char):
                    temp = command_word
                    for i in range(len(self.minus_char)):
                        temp[i] = ''
                        
                    if temp in self.toggle_commands:
                        self.toggle_commands.erase(temp)
                        self._on_toggle_commands_erased(temp)
                        temp = None
                
                for i in range(len(self.aliases[command_word])):
                    args = None
                    if self.return_char in self.aliases[command_word][i]:
                        new_command = ''
                        ignore_until = -1
                        for c_i in range(len(self.aliases[command_word][i])):
                            if ignore_until < c_i:
                                if self.aliases[command_word][i][c_i] == self.return_char:
                                    temp = ''
                                    end_index = self.aliases[command_word][i].find(' ', c_i)
                                    
                                    if end_index != -1:
                                        ignore_until = c_i-1
                                        for c_ii in range(end_index-c_i):
                                            temp += self.aliases[command_word][i][c_i+c_ii]
                                            ignore_until += 1
                                    else:
                                        end_index = len(self.aliases[command_word][i])-c_i
                                        ignore_until = c_i-1
                                        for c_ii in range(end_index):
                                            temp += self.aliases[command_word][i][c_i+c_ii]
                                            ignore_until += 1
                                    
                                    for ivar in self.incrementvariables:
                                        if self.return_char+ivar == temp:
                                            new_command += str(self.incrementvariables[ivar].get_value())
                                            break
                                else:
                                    new_command += self.aliases[command_word][i][c_i]
                        
                        args = new_command
                    else:
                        args = self.aliases[command_word][i]
                    
                    self.execute(args)
                    self.set_running_command(args)
                self.set_running_command(command_word)
                return
            
            for c in self.incrementvariables.copy():
                if c == command_word:
                    self.incrementvariables[c].increment()
                    return
                
                if self.return_char+c == command_word:
                    out = handle_input(str(self.incrementvariables[c].get_value()))
                    if out == None or out[1] == self.colors['output']['error']: # no momento é a unica forma de eu pegar se for erro...
                        return # vai retornar se for erro
                    return out # se nao for erro, vai retornar a str
            
            if command_word in self.loop_aliases:
                if command_word in self.loop_aliases_on:
                    self.loop_aliases_on.remove(command_word)
                else:
                    self.loop_aliases_on.append(command_word)
                return
        
        return ['Unknown command: "' + command_word + '"', self.colors['output']['error']]

    def alias(self, args: list):
        alias_name = args[0]
        args.pop(0)
        
        alias_name_plus = None
        if alias_name.startswith(self.plus_char) and len(self.plus_char) != len(alias_name):
            alias_name_plus = alias_name
            for i in range(len(self.plus_char)):
                alias_name_plus[i] = ''
            if self.minus_char+alias_name_plus in self.aliases:
                pass
            else:
                self.aliases[self.minus_char+alias_name_plus] = []
        
        args = self.split_alias(args)
        
        for arg in args: # add -arg for each +arg in alias to the negative alias_name array
            if alias_name_plus != None and arg.startswith(self.plus_char) and len(self.plus_char) != len(arg):
                if ' ' not in arg:
                    temp = arg
                    for i in range(len(self.plus_char)):
                        temp[i] = ''
                    if arg not in self.aliases[self.minus_char+alias_name_plus]:
                        self.aliases[self.minus_char+alias_name_plus].append(self.minus_char+temp)
        
        self.aliases[alias_name] = args

    def get_aliases(self):
        output = ''
        for alias in self.aliases:
            output += alias + '\n'
        
        index = 0
        for alias in self.loop_aliases:
            if index == len(self.loop_aliases)-1:
                output += alias
            else:
                output += alias + '\n'
        
        if len(self.loop_aliases) == 0: # remove \n made by the first for-loop
            output = output[:-1]

        return output

    def loop_alias(self, args):
        alias_name = args[0]
        args.pop(0)

        if alias_name in self.aliases:
            self.aliases.pop(alias_name)

        args = self.split_alias(args)
        self.loop_aliases[alias_name] = args

    def get_loop_aliases(self):
        output = ''
        index = 0
        for alias in self.loop_aliases:
            if index == len(self.aliases):
                output += alias
            else:
                output += alias + '\n'
            index += 1
        return output

    def get_commands(self):
        output = ''
        index = 0
        for command in self.valid_commands:
            if self.valid_commands[command][3] != None:
                if index == len(self.valid_commands)-1:
                    output += self.valid_commands[command][3]
                else:
                    output += self.valid_commands[command][3] + '\n'
                index += 1
        return output

    def update(self):
        for command in self.loop_aliases_on:
            if command in self.loop_aliases:
                if len(self.loop_aliases[command]) == 1 and self.loop_aliases[command][0] == '':
                    self.loop_aliases_on.remove(command)

                for c in self.loop_aliases[command]:
                    self.execute(c)
    
    def execute(self, command: str):
        out = self.handle_input(command.strip())
        if out == None:
            return
        
        if type(out) == str:
            self.output_text(out)
        else:
            self.output_text(out[0], out[1])

    def output_text(self, text: str, text_color: tuple=None):
        if text == None or text.lower().strip().replace('\n','') == 'none':
            return
        
        if text_color == None :
            text_color = self.colors['output']['default']

        # todo: pass the text to pygame/tkinter window AND put the text_color
        print(text)

    def create_incrementvar(value, var_name, minvalue, maxvalue, delta):
        self.incrementvariables[var_name] = IncrementVariable(value, minvalue, maxvalue, delta)

    def _help(self, command: str):
        if command in self.valid_commands:
            if self.valid_commands[command][3] == None:
                return command + ' does not have a description.'
            return self.valid_commands[command][3]
        return command + ' does not exists.'

    def echo(self, args):
        output = ''
        for i in args:
            output += str(i) + ' '
        return output[:-1]
    
    def set_running_command(self, command: str):
        if command not in self.running_commands:
            self.running_commands.append(command)

    def split_alias(self, args: str):
        temp = ''
        for i in args:
            temp += str(i).strip() + ' '
            
        args = temp.split(self.alias_separator)
        for i in range(len(args)):
            args[i] = args[i].strip()
        
        return args

    def exec_cfg(self, file_path: str):
        file_path = convert_path(file_path)

        if not os.path.exists(file_path):
            if os.path.exists(file_path+'.cfg'):
                file_path += '.cfg'
                if not os.path.isfile(file_path):
                    raise OSError(f'{file_path} is not a file.')
            else:
                return ['File does not exists', self.colors['output']['error']]

        if not os.path.exists(file_path):
            file_path = self.cfg_path+os.path.sep+file_path
        
        with open(file_path, 'r') as f:
            content = f.read().split('\n')
        
        for i in range(len(content)):
            if content[i].startswith('//'):
                content.pop(i)
                
            index = 0
            bar_index = -1
            temp = ''
            for c in content[i]:
                if c == '/':
                    if bar_index != -1:
                        if index == bar_index+1:
                            break
                    else:
                        if len(content[i])-1 != index:
                            if content[i][index+1] != '/':
                                temp += c
                        else:
                            temp += c
                    bar_index = index
                else:
                    temp += c
                index += 1
            content[i] = temp.rstrip()

        for line in content:
            self.execute(line)

    def check_toggle_commands(self):
        for i in self.toggle_commands:
            self.execute(self.plus_char+i)

    def command_just_ran(self, command):
        if command in self.running_commands:
            return True
        return False

    def erase_running_commands(self):
        temp = []
        for command in self.ignore_commands:
            if command in self.running_commands:
                temp.append(command)

        self.running_commands = temp

    def quit(self):
        self.running = False

    def loop_update(self):
        while self.running:
            sleep(0.00015)
            self.update()

    def handle_lines(self, command):
        for line in command.split(self.separator):
            self.execute(line)

    def run(self):
        self.output_text(f'{NAME} V{VERSION} (Python {sys.version})', (0,255,0))
        self.running = True

        t = Thread(target=self.loop_update)
        t.start()
        while self.running:
            command = input('>')

            self.threads.append(Thread(target=self.handle_lines, args=[command]))
            self.threads[-1].start()

if __name__ == '__main__':
    console = Console()
    console.run()
