import yaml
import task_lib
from cmd_event import cmd_event

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
			if (curr.process and curr.process.pid == int(line)):
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
				self.cmd[name] = task_lib.dup(self.cmd[k])
				self.cmd[name].id = name
				self.cmd[name].parent = self.cmd[k]
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
				if (cmd.status == "WAITING" or cmd.status == "FAILED"):
					cmd.start(False);
					cmd.show_status()
				elif (cmd.status == "RUNNING" or cmd.status == "STARTING"):
					print ("task: Command " + line + " already STARTING/RUNNING")
				else:
					print ("task: FATAL_ERROR: " + cmd.id)
				break
		if (find == False):
			print ("task: no process found " + line)

	def	restart(self, line):
		curr = check_pid(self.cmd, line)
		if (curr != None):
			curr.restart()
			curr.show_status()
		else:
			print ("task: no process found " + line)

	def	stop(self, line):
		curr = check_pid(self.cmd, line)
		if (curr != None):
			curr.stop()
			curr.show_status()
		else:
			print ("task: no process found " + line)

	def	status(self):
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
				cmd.finish(sig_num);
			elif (cmd.process and cmd.stop_timer >= 0):
				if (cmd.stop_timer >= cmd.stoptime):
					cmd.process.send_signal(9);
					print ("process killed")
				else:
					cmd.stop_timer += 1
			elif (cmd.process and cmd.start_timer >=0):
				if (cmd.start_timer >= cmd.starttime):
					cmd.start_timer = -1
					cmd.status = "RUNNING"
				else:
					cmd.start_timer += 1