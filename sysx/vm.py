'''
	functionCase
	variable_case
	ClassCase
'''

'''
	Machine:
		- 16 registers (can hold $, %, @)
		- A Stack (16)
		- Memory Array (8 * 8) [$, %, @]
		- An Instruction Pointer
		- A Stack Pointer

	Todo:
		- Streamline Error Handling.
'''

import math

class InvalidInstruction:
	pass

class InvalidRegister:
	pass

class Register:
	def __init__(self):
		self.__intpart = 0
		self.__strpart = '(null)'
		self.__fltpart = 0.0

	def getReg(self, reg_type):
		if reg_type == '%':
			return self.__intpart
		elif reg_type == '$':
			return self.__strpart
		elif reg_type == '@':
			return self.__fltpart

	def setReg(self, reg_type, value):
		if reg_type == '%':
			if (type(value) == str and value.isnumeric()) or (type(value) == int):
				self.__intpart = int(value)
		elif reg_type == '$':
			self.__strpart = str(value)
		elif reg_type == '@':
			if (type(value) == str and value.replace('.', '').isnumeric()) or (type(value) == float or type(value) == int):
				self.__fltpart = float(value)
		else:
			print("Error: {} is not a valid value for {}.".format(value, reg_type))

	def resetReg(self):
		self.__init__()

	def __str__(self):
		return "{} {} {}".format(str(self.__intpart).ljust(8), self.__strpart.ljust(16), str(self.__fltpart).ljust(8))

def identifyRegister(character):
	if character.isdigit():
		return int(character)
	else:
		if ord(character) <= ord('F'):
			return ord(character) - 55
			'''
				Because or d('A') = 65, and since
				we need 'A' to be 10, we do: 65 - x = 10
				and x = 55
			'''
		else:
			return -1

def validRegType(reg_type):
	return reg_type in ['$', '%', '@']

class Stack:
	def __init__(self):
		self.__stack = []
		self.__top = -1
		self.__MAX_SIZE = 16

	def isFull(self):
		return self.__top == self.__MAX_SIZE -1

	def isEmpty(self):
		return self.__top == -1

	def push(self, value):
		if not self.isFull():
			self.__stack.append(value)
			self.__top += 1

	def pop(self):
		if not self.isEmpty():
			self.__stack.pop()
			self.__top -= 1

	def peek(self):
		if self.isEmpty():
			return
		return self.__stack[-1]

	def getTop(self):
		return self.__top

	def printStack(self):
		if self.isEmpty():
			return

		print(self.__stack[-1], "<- Top")
		for i in range(len(self.__stack) - 2, -1, -1):
			print(self.__stack[i])

class VirtualMachine:
	def __init__(self):
		self.__registers = []

		for i in range(0, 16):
			self.__registers.append(Register())

		'''
			We run a for-loop instead
			self.__register = [Register()] * 16, because
			it otherwise copies the same reference. And that
			would cause all registers to point to a single register,
			making them have the same values. Same for self.__mem_array.
		'''

		self.__stack = Stack()
		self.__mem_array = []

		for i in range(0, 8):
			self.__mem_array.append([0] * 8)

		self.__ip = 0

		self.__running = False
		self.__program = []
		self.__section_dict = {}

	# Soft Reset - Resets only the memory, regs, etc. Not the program.
	# Hard Reset - Just use __init__()

	def softReset(self):

		for register in self.__registers:
			register.resetReg()

		self.__stack = Stack()
		
		for i in range(0, 8):
			for j in range(0, 8):
				self.__mem_array[i][j] = 0

		self.__ip = 0
		self.__running = False

		self.__section_dict.clear()

	def loadProgram(self, program):
		self.__program = program.copy()

	def preprocessCode(self):

		for i in range(len(self.__program)):
			args = self.__program[i].split()

			if len(args) >= 2:
				command = args[0]

				if command == "_SECTION":
					if args[1] in self.__section_dict:
						print("Error: Two sections of the same name cannot exist.")
						print("Preprocessing failed.")

						return False

					else:
						self.__section_dict[args[1]] = i
						self.__program[i] = 'NOTE ({})'.format(self.__program[i])

		return True

	def printString(self, string):
		i = 0
		while i < len(string):
			if string[i] == '^':
				if i == len(string) - 1:
					print("Error: Missing escape character.")
				else:
					if string[i + 1] == 'S':
						print(' ', end = ""); i += 1
					elif string[i + 1] == 'T':
						print('\t', end = ""); i += 1
					elif string[i + 1] == 'N':
						print('\n', end = ""); i += 1
					else:
						print("Error: {} is not a valid escape character.".format(string[i + 1]))
			else:
				print(string[i], end = "")

			i += 1

	def executeInstruction(self, instruction):
		# Decode Instruction
		args = instruction.split()

		if len(args) == 0:
			return
		else:
			command = args[0]
			args.pop(0)

		# Execute Instruction
		if command == "HALT":
			self.__running = False
			return

		elif command == "PRINT":
			if len(args) >= 1:
				args = ' '.join(args)
				self.printString(args)
			else:
				print()

		elif command == "GET":
			if len(args) == 1:
				reg_type = args[0][0]
				reg_index = identifyRegister(args[0][1])

				if validRegType(reg_type) and reg_index != -1:
					if reg_type == '$':
						self.printString(self.__registers[reg_index].getReg(reg_type))
					else:
						print(self.__registers[reg_index].getReg(reg_type), end = "")
				else:
					print("Error: '{}' is not a valid register".format(args[0]))

			else:
				print("Error: Invalid number of arguments.")

		elif command == "SET":
			if len(args) >= 2:
				reg_type = args[0][0]
				reg_index = identifyRegister(args[0][1])

				if validRegType(reg_type) and reg_index != -1:
					args.pop(0)
					self.__registers[reg_index].setReg(reg_type, ' '.join(args))
				else:
					print("Error: '{}' is not a valid register".format(args[0]))

			else:
				print("Error: Invalid number of arguments.")

		elif command == "GOTO":
			if len(args) == 1:
				if args[0].isnumeric():
					line_number = int(args[0])
					if line_number in range(0, len(self.__program)):
						self.__ip = line_number

				else:
					if args[0] in self.__section_dict:
						self.__ip = self.__section_dict[args[0]]
					else:
						print("Error: {} is not a valid section.".format(args[0]))

		# Arithmetic Instructions
		elif command == "ADD":
			if len(args) == 2:
				reg1_type = args[0][0]
				reg1_index = identifyRegister(args[0][1])

				if validRegType(reg1_type) and reg1_index != -1:
					reg2_type = args[1][0]

					# Immediate Arithmetic
					if reg2_type == '#':
						lvalue = self.__registers[reg1_index].getReg(reg1_type)

						# Remember that Register F will be used for Intermediate Arithmetic.
						# They will be automatically cleared after the operation, but still
						# be careful to not make a collision somehow.

						self.__registers[identifyRegister('F')].setReg(reg1_type, args[1][1:])
						rvalue = self.__registers[identifyRegister('F')].getReg(reg1_type)
						self.__registers[reg1_index].setReg(reg1_type, lvalue + rvalue)

						# Clearing Register F

						self.__registers[identifyRegister('F')].resetReg()

					# Register Arithmetic
					else:
						reg2_index = identifyRegister(args[1][1])
						if validRegType(reg2_type) and reg2_index != -1:
							if reg1_type == reg2_type:
								lvalue = self.__registers[reg1_index].getReg(reg1_type)
								rvalue = self.__registers[reg2_index].getReg(reg1_type)
								self.__registers[reg1_index].setReg(reg1_type, lvalue + rvalue)

							else:
								print("Error: Cannot add {} and {}.".format(reg1_type, reg2_type))

						else:
							print("Error: '{}' is not a valid register".format(args[1]))
							raise InvalidRegister

				else:
					print("Error: '{}' is not a valid register".format(args[0]))
					raise InvalidRegister()
			else:
				print("Error: Invalid number of arguments.")

		elif command == "SUB":
			pass
		elif command == "MUL":
			pass
		elif command == "DIV":
			pass

		elif command in ["NOTE", "--"]:
			pass

		# Debugging Instructions
		# So that I would'nt have to invoke the functions from here.

		elif command in ["_DEBUG_VIEW_REG", "DBR"]:
			self.printRegs()

		elif command in ["_DEBUG_VIEW_MEM", "DBM"]:
			self.printMemArray()

		elif command in ["_DEBUG_RESET", "DBRST", "_INIT_VM"]:
			self.softReset()

		else:
			print("Error: Line ({}) '{}' not understood.".format(self.__ip, command))
			raise InvalidInstruction

	def runProgram(self):

		self.__running = True
		
		while self.__running:
			instruction = self.__program[self.__ip]
			self.executeInstruction(instruction)
			self.__ip += 1

	# Debugging Functions

	def loadProgamFromMemory(self, filename):
		file = open(filename, "r")

		program = []
		
		while file:
			line  = file.readline()
			if not line:
				break

			program.append(line.rstrip())

		self.loadProgram(program)

		file.close()

	def playground(self):

		self.loadProgamFromMemory("arithmetic")

		try:
			if not self.preprocessCode():
				return

			print("Program: ")
			self.printProgram()
			print()

			print("Output:")

			self.runProgram()
			print("\nMessage: Successfully executed.")

		except:
			print("\nMessage: Program terminated prematurely at line ({}).".format(self.__ip))
			self.__running = False

	def printProgram(self):

		'''
			Max-width defines the width, that is, the
			number of digits of the total length of the
			program. We need this, so that we can properly
			format the line-numbers when printing the program.
		'''

		max_width = int(math.log10(len(self.__program))) + 1

		for i in range(len(self.__program)):
			print('[' + str(i).rjust(max_width) + ']', self.__program[i])

	def printMemArray(self):
		for i in range(0, 8):
			for j in range(0, 8):
				print(self.__mem_array[i][j], end = " ")
			print()

	def printRegs(self):
		print("{} {} {}".format("%".ljust(8), "$".ljust(16), "@".ljust(8)))
		print("-" * (8 + 16 + 8))
		for register in self.__registers:
			print(register)

vm = VirtualMachine()
vm.playground()
