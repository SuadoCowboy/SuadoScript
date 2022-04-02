import os

NAME = 'SCCP'
VERSION = '0.0.1' # alpha

def convert_path(path: str, separators: list=['\\','/']):
	for i in items:
		path = path.replace(i, os.path.sep)
	return path

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

class Console:
	def __init__(self, separator: str=';', cfg_path: str='./cfg'):
		self.colors = {
			'output_error_font_color':(255,0,0),
			'output_font_color':(255,255,255)
		}

		self.cfg_path = cfg_path
		self.cfg_configfile = 'config.cfg'

		self.separator = separator
		self.alias_separator = '&&'
		self.return_char = '@'
		self.plus_char = '+'
		self.minus_char = '-'

		self.aliases = {}
		self.loop_aliases = {}
		self.loop_aliases_on = []

		self.incrementvariables = {}

		self.running_commands = []
		self.ignore_commands = []
		self.toggle_commands = []

	def handle_input(self, text):
		words = text.lstrip().rstrip().split()

		if len(words) == 0:
			return
		
		command_word = words[0]
		words.pop(0)
		if command_word in self.valid_commands:
			c = self.valid_commands[command_word]
			if c[1] == False: # is_multiple_args check
				if len(words) != len(c[2]): # da erro se estiver faltando argumentos ou tiver muitos argumentos
					return [str('Failure executing command "', command_word, '" expected ', len(c[2]), ' parameters'), self.colors['output_error_font_color']]
			
			checktype = None
			for i in range(len(words)):
				if command_word in CommandHandler.returnchar_valid_commands:
					pass
				else:
					if words[i].begins_with(Global.return_char):
						for cc in Global.incrementvariables.duplicate():
							if words[i] == str(Global.return_char, cc):
								words[i] = str(Global.incrementvariables[cc].get_value())
					
				if c[1] == True:
					checktype = check_type(words[i], c[2][0])
				else:
					checktype = check_type(words[i], c[2][i])
					
				if not checktype:
					return [str('Failure executing command "', command_word, '" parameter ', i+1, ' "', words[i], '" is the wrong type'), Global.ui_custom['console']['output_error_font_color']]
				
			if c[1] == True:
				words = [words]
			
			Global.set_running_command(command_word)
			return CommandHandler.callv(c[0], words)
		
		if len(words) == 0: # se for só command_word ou seja n tem arg
			if command_word in Global.aliases: # se loop de alias funciona, por que de alias nao?
				if command_word.begins_with(Global.plus_char) and len(command_word) != len(Global.plus_char):
					temp = command_word
					for i in range(len(Global.plus_char)):
						temp[i] = ''
					
					if temp in Global.toggle_commands:
						pass
					else:
						Global.toggle_commands.append(temp)
						temp = null
				elif command_word.begins_with(Global.minus_char) and len(command_word) != len(Global.minus_char):
					temp = command_word
					for i in range(len(Global.minus_char)):
						temp[i] = ''
						
					if temp in Global.toggle_commands:
						Global.toggle_commands.erase(temp)
						Global._on_toggle_commands_erased(temp)
						temp = null
				
				for i in range(len(Global.aliases[command_word])):
					args = null
					if Global.return_char in Global.aliases[command_word][i]:
						new_command = ''
						ignore_until = -1
						for c_i in range(len(Global.aliases[command_word][i])):
							if ignore_until < c_i:
								if Global.aliases[command_word][i][c_i] == Global.return_char:
									temp = ''
									end_index = Global.aliases[command_word][i].find(' ', c_i)
									
									if end_index != -1:
										ignore_until = c_i-1
										for c_ii in range(end_index-c_i):
											temp += Global.aliases[command_word][i][c_i+c_ii]
											ignore_until += 1
									else:
										end_index = len(Global.aliases[command_word][i])-c_i
										ignore_until = c_i-1
										for c_ii in range(end_index):
											temp += Global.aliases[command_word][i][c_i+c_ii]
											ignore_until += 1
									
									for ivar in Global.incrementvariables:
										if Global.return_char+ivar == temp:
											new_command += str(Global.incrementvariables[ivar].get_value())
											break
								else:
									new_command += Global.aliases[command_word][i][c_i]
						
						args = new_command
					else:
						args = Global.aliases[command_word][i]
					
					execute(args)
					Global.set_running_command(args)
				Global.set_running_command(command_word)
				return
			
			for c in Global.incrementvariables.duplicate():
				if c == command_word:
					Global.incrementvariables[c].increment()
					return
				
				if Global.return_char+c == command_word:
					out = handle_input(str(Global.incrementvariables[c].get_value()))
					if out == null or out[1] == Global.ui_custom['console']['output_error_font_color']: # no momento é a unica forma de eu pegar se for erro...
						return # vai retornar se for erro
					return out # se nao for erro, vai retornar a str
			
			if command_word in Global.loop_aliases:
				if command_word in Global.loop_aliases_on:
					Global.loop_aliases_on.erase(command_word)
				else:
					Global.loop_aliases_on.append(command_word)
				return
		
		return [str('Unknown command: "', command_word, '"'), Global.ui_custom['console']['output_error_font_color']]

	def update(self):
		for command in self.loop_aliases_on:
			if command in self.loop_aliases:
				for c in self.loop_aliases[command]:
					self.execute(c)
	
	def execute(self, command: str):
		out = self.handle_input(command.lstrip().rstrip())
		if out == None:
			return
		
		if type(out) == str:
			self.output_text(out)
		else:
			self.output_text(out[0], out[1])

	def output_text(self, text: str, text_color: str=None):
		if text == None or text.lower().rstrip().lstrip().replace('\n','') == 'none':
			return
		
		if text_color == None:
			text_color = self.colors['output_font_color']

		# todo: pass the text to pygame window

def split_alias(console: Console, args: str):
	temp = ''
	for i in args:
		temp += str(i).lstrip().rstrip() + ' '
		
	args = temp.split(console.alias_separator)
	for i in range(len(args)):
		args[i] = args[i].lstrip().rstrip()
	
	return args

def exec_cfg(console: Console, file_path: str):
	file_path = console.cfg_path+'/'+file_path
	
	if not os.path.exists(file_path):
		if os.path.exists(file_path+'.cfg'):
			file_path += '.cfg'
		else:
			return ['File does not exists', console.colors['output_error_font_color']]
	
	with open(file_path, 'r') as f:
		content = f.readlines().split('\n')
	
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
		console.execute(line)

def check_toggle_commands(console: Console):
	for i in console.toggle_commands:
		console.execute(console.plus_char+i)

def command_just_ran(console: Console, command):
	if command in console.running_commands:
		return True
	return False

def erase_running_commands(console: Console):
	temp = []
	for command in console.ignore_commands:
		if command in console.running_commands:
			temp.append(command)

	console.running_commands = temp

def set_running_command(console: Console, command):
	if command not in running_commands:
		console.running_commands.append(command)