import task_lib
from cmd_event import cmd_event

class task_event:

	def __init__(self):
		data = task_lib.load_conf("config.yaml")
		cmd = data.get("programs")
		self.cmd = {}
		i = 1
		for k, v in cmd.iteritems():
			cmd_class = cmd_event(k, v)
			self.cmd[k] = cmd_class
			while (i < cmd_class.numprocs):
				name = k + ":0" + str(i)
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
			if (line and (line == cmd.id or line == "all")):
				find = True
				if (cmd.status == "WAITING" or cmd.status == "FAILED" or cmd.status == "STOPPED"):
					cmd.start(False);
					cmd.show_status()
				elif (cmd.status == "RUNNING" or cmd.status == "STARTING" or cmd.status == "STOPPING"): ####
					print (cmd.id + " is already actived or stopping")
				else:
					print ("FATAL_ERROR: " + cmd.id)
				if (line != "all"):
					break
		if (find == False):
			print ("task: no process found " + line)

	def	restart(self, line):
		if (str(line) == "all"):
			for k, v in self.cmd.iteritems():
				cmd = self.cmd[k]
				if (cmd.process != None): ####
					cmd.restart()
					cmd.show_status()
		else:
			curr = task_lib.check_process(self.cmd, line)
			if (curr != None):
				curr.restart()
				curr.show_status()
			else:
				print ("task: no process running found -> check status" + line)

	def	stop(self, line):
		if (str(line) == "all"):
			for k, v in self.cmd.iteritems():
				cmd = self.cmd[k]
				if (cmd.process != None): ####
					cmd.stop()
					cmd.show_status()
					cmd.time = 0
		else:
			curr = task_lib.check_process(self.cmd, line)
			if (curr != None):
				curr.stop()
				curr.show_status()
				curr.time = 0
			else:
				print ("task: no process running found -> check status" + line)

	def info(self, line):
		if (line):
			for k, v in self.cmd.iteritems():
				cmd = self.cmd[k]
				if (cmd.id == str(line)):
					task_lib.print_all_info(cmd, line)
					break
		else:
			print ("info requiere a target")

	def	status(self, line):
		find = False
		if (line):
			for k, v in self.cmd.iteritems():
				cmd = self.cmd[k]
				if (cmd.id == str(line)):
					find = True
					cmd.show_status()
					break
		else:
			find = True
			for k, v in self.cmd.iteritems():
				cmd = self.cmd[k]
				cmd.show_status()
		if (find == False):
			print ("task: no process found " + line)

	def reload(self):
		task_lib.close_fd(self.cmd)
		new_task = task_event()
		for k, v in self.cmd.iteritems():
			i = 0;
			cmd = self.cmd[k]
			for l, w in new_task.cmd.iteritems():
				cmd_comp = new_task.cmd[l]
				if (cmd.id == cmd_comp.id):
					i = 1
					if (cmd.path == cmd_comp.path and cmd.stdout == cmd_comp.stdout and cmd.stderr == cmd_comp.stderr and cmd.workingdir == cmd_comp.workingdir):

						if (cmd.status == "RUNNING" or cmd.status == "STARTING"):
							new_task.cmd[l].process = cmd.process
							new_task.cmd[l].status = cmd.status
							new_task.cmd[l].state = cmd.state
							new_task.cmd[l].start_timer = cmd.start_timer
							new_task.cmd[l].stop_timer = cmd.stop_timer
							new_task.cmd[l].start_fail = new_task.cmd[l].start_fail

						elif (cmd.status == "WAITING" or cmd.status == "STOPPED"):
							if (cmd_comp.autostart == True):
								cmd_comp.start(True)
						break

					elif (cmd.process):
						cmd.stop_signal = 9
						cmd.stop()
						cmd_comp.start(True)
			if (i == 0 and cmd.process):
				cmd.stop_signal = 9
				cmd.stop()

		for a, b in new_task.cmd.iteritems():
				cmd_comp = new_task.cmd[a]
				if (cmd_comp.autostart == True and cmd_comp.status == "WAITING" and cmd_comp.process == None):
					cmd_comp.start(True)

		self.cmd = new_task.cmd
		self.status(None)

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
					task_lib.log.warning(cmd.id + ': has been kill due to config: stoptime')
				else:
					cmd.stop_timer += 1
			elif (cmd.process and cmd.start_timer >=0):
				if (cmd.start_timer >= cmd.starttime):
					cmd.start_timer = -1
					cmd.status = "RUNNING"
				else:
					cmd.start_timer += 1