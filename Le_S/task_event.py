import yaml
from cmd_event import cmd_event
import copy
import pyautogui



def load_conf(file):
	try:
		fd = open(file, "r")
		data = yaml.load(fd)
		return data
	except Exception, e:
		print("error config -> " + file)

def check_pid(cmd, line):
	try:
		for k, v in cmd.iteritems():
			curr = cmd[k]
			if (curr.id == str(line) and curr.process):
				return (curr)
	except Exception, e:
		return (None)

class task_event:

	def __init__(self):
		data = load_conf("config.yaml")
		cmd = data.get("programs")
		self.cmd = {}
		i = 1
		for k, v in cmd.iteritems():
			cmd_class = cmd_event(k, v)
			self.cmd[k] = cmd_class
			while (i < cmd_class.numprocs):
				name = k + str(i)
				self.cmd[name] = cmd_event(name, v)
				i += 1

	def	autostart(self):
		for k, v in self.cmd.iteritems():
			cmd = self.cmd[k]
			if (cmd.autostart):
				cmd.start(True)

	def	start(self, line):
		find = False
		for k, v in self.cmd.iteritems():
			cmd = self.cmd[k]
			if (line and cmd.id == line):
				find = True
				if (cmd.status == "WAITING"):
					cmd.start(False);
				elif (cmd.status == "RUNNING"):
					print ("task: Command " + line + " already RUNNING")
				break
		if (find == False):
			print ("task: no process found " + line)

	def	restart(self, line):
		if (str(line) == "all"):
			for k, v in self.cmd.iteritems():
				cmd = self.cmd[k]
				curr = check_pid(self.cmd, cmd.id)
				if (curr != None):
					curr.restart()
		else:
			curr = check_pid(self.cmd, line)
			if (curr != None):
				curr.restart()
			else:
				print ("task: no process found " + line)

	def	stop(self, line):
		curr = check_pid(self.cmd, line)
		if (curr != None):
			curr.stop()
		else:
			print ("task: no process found " + line)

	def	status(self, line):
		# if (line):
		# 	for k, v in self.cmd.iteritems():
		# 		cmd = self.cmd[k]
		# 		if (str(cmd.id) == str(line))
		# 			cmd.show_status()
		# 			break
		# else:
			for k, v in self.cmd.iteritems():
				cmd = self.cmd[k]
				cmd.show_status()

	def check_status(self):
		for k, v in self.cmd.iteritems():
			cmd = self.cmd[k]
			if (cmd.process and cmd.process.poll()):
				sig_num = cmd.process.returncode
				if (sig_num < 0):
					sig_num *= -1
				print("")
				cmd.finish(sig_num);
				pyautogui.press('enter')
			elif (cmd.process and cmd.stop_timer >= 0):
				if (cmd.stop_timer >= cmd.stoptime):
					cmd.process.send_signal(9) ;
					print ("\nprocess killed")
					pyautogui.press('enter')
				else:
					cmd.stop_timer += 1
			elif (cmd.process and cmd.start_timer >=0):
				if (cmd.start_timer >= cmd.starttime):
					cmd.start_timer = -1
					cmd.status = "RUNNING"
					print ("")
					cmd.show_status()
					pyautogui.press('enter')
				else:
					cmd.start_timer += 1

	def reload(self):
		new_task = task_event()
		for k, v in self.cmd.iteritems():
			i = 0;
			cmd = self.cmd[k]
		#
			for l, w in new_task.cmd.iteritems():
				cmd_comp = new_task.cmd[l]
		#	#
				if (cmd.id == cmd_comp.id):
					i = 1
		#	#	#
					if (cmd.path == cmd_comp.path and cmd.stdout == cmd_comp.stdout and cmd.stderr == cmd_comp.stderr and cmd.workingdir == cmd_comp.workingdir):

						if (cmd.status == "RUNNING"):
							cmd_comp = copy.deepcopy(cmd)
							new_task.cmd[l] = cmd_comp
						elif (cmd.status == "WAITING"):
							if (cmd_comp.autostart == True):
								cmd_comp.start(True)
						break

					elif (cmd.process):
						cmd.stop()
						cmd_comp.start(True)

		#	#	#
			if (i == 0 and cmd.process):
				cmd.stop()
		self.cmd = new_task.cmd

		for a, b in new_task.cmd.iteritems():
				cmd_comp = new_task.cmd[a]
				if (cmd_comp.autostart == True and cmd_comp.status == "WAITING" and cmd_comp.process == None):
					cmd_comp.start(True)

		self.status()
