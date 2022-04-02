import os

NAME = 'SCCP'
VERSION = '0.0.1' # alpha

def convert_path(path: str, separators: list=['\\','/']):
	for i in items:
		path = path.replace(i, os.path.sep)
	return path

class Console:
	def __init__(self, separator: str=';', cfg_path: str='./cfg'):
		self.colors = {
			'error':(255,0,0),
			'default':(255,255,255)
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

	def update(self):
		for command in self.loop_aliases_on:
			if command in self.loop_aliases:
				for c in self.loop_aliases[command]:
					self.execute(c)
	
	def execute(self, command: str):
		out = self.handle_input(command.lstrip(' ').rstrip(' '))
		if out == None:
			return
		
		if type(out) == str:
			self.output_text(out)
		else:
			self.output_text(out[0], out[1])

	def output_text(self, text: str, text_color: str=None):
		if text == None or text.lower().rstrip(' ').lstrip(' ').replace('\n','') == 'None':
			return
		
		if text_color == null:
			text_color = Global.ui_custom['console']['output_font_color']
		
		output_box.push_color(text_color)
		output_box.append_bbcode(str('\n', text))
		output_box.pop()
		
		output_box.scroll_to_line(output_box.get_line_count()-1)

def split_alias(console: Console, args: str):
	temp = ''
	for i in args:
		temp += str(i).lstrip(' ').rstrip(' ') + ' '
		
	args = temp.split(console.alias_separator)
	for i in range(len(args)):
		args[i] = args[i].lstrip(' ').rstrip(' ')
	
	return args

def exec_cfg(console: Console, file_path: str):
	file_path = console.cfg_path+'/'+file_path
	
	if not os.path.exists(file_path):
		if os.path.exists(file_path+'.cfg'):
			file_path += '.cfg'
		else:
			return [console.colors['error'], 'File does not exists']
	
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
		content[i] = temp.rstrip(' ')
	
	for line in content:
		console.execute(line)

def check_toggle_commands(console: Console):
	for i in console.toggle_commands:
		console.execute(console.plus_char+i)

def command_just_ran(console: Console, command):
	if command in console.running_commands:
		return true
	return false

def erase_running_commands(console: Console):
	temp = []
	for command in console.ignore_commands:
		if command in console.running_commands:
			temp.append(command)

	console.running_commands = temp

def set_running_command(console: Console, command):
	if command not in running_commands:
		console.running_commands.append(command)