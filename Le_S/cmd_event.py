import os
import stat
import time
import shlex
import subprocess
import task_lib

def check_path(path):
	print ("need to check if " + path + " exist")
	return (True)

def special_params(cmd, params, name):
	if (name == "autorestart"):
		if ((type(params[name]) is int and params[name] < 0) or params[name] != "unexpected"):
			cmd.state = "wrong autorestart data"
			return (False)
	elif (name == "exitcodes"):
		if (type(params[name]) is not list):
			return (False)
		for exit in params[name]:
			if ((type(exit) is int and exit < 0) or type(exit) is not int):
				cmd.state = "wrong exit data"
				return (False)
	return (True)

def check_validity(cmd, params, name):
	type_define = {
		"cmd": str,
		"workingdir": str,
		"stopsignal": str,
		"stdout": str,
		"stderr": str,
		"autostart": bool,
		"starttime": int,
		"startretries": int,
		"stoptime": int,
		"numprocs": int,
	}
	if (name == "autorestart" or name == "exitcodes"):
		return (special_params(cmd, params, name))
	elif (type(params[name]) is type_define[name]):
		if (type_define[name] is int and params[name] < 0):
			cmd.state = "positive value expected -> " + name
			return (False)
		elif (type_define[name] is str):
			if (name == "stopsignal"):
				ret = task_lib.signaux.get_signum(params[name])
				if (ret < 0 or ret > 30):
					cmd.state = "wrong signal -> " + name
					return (False)
			elif (check_path(params[name]) == False):
				cmd.state = "wrong path -> " + params[name]
				return (False)
	elif (type(params[name]) is not type_define[name]):
		cmd.state = "wrong type params -> " + name
		return (False)
	return (True)

def in_config(cmd, params, name):
	if (params):
		for k, v in params.iteritems():
			if (k == name and check_validity(cmd, params, name) == True):
				return (params[name])
	return None

class cmd_event:

	def __init__(self, key, params):
		self.id = key
		self.status = "WAITING"
		self.state = "NOT STARTING"
		self.path = in_config(self, params, "cmd") or "/ERROR"
		self.workingdir = in_config(self, params, "workingdir") or "/tmp"
		self.numprocs = in_config(self, params, "numprocs") or 1
		self.stdout = in_config(self, params, "stdout") or "/tmp/task_STDOUT"
		self.stderr = in_config(self, params, "stderr") or "/tmp/task_STDERR"
		self.autostart = in_config(self, params, "autostart")
		self.autorestart = in_config(self, params, "autorestart") or "unexpected"
		self.exit = in_config(self, params, "exitcodes") or [0, 2]
		self.starttime = in_config(self, params, "starttime") or 1
		self.start_timer = -1
		self.startretries = in_config(self, params, "startretries") or 1
		self.start_fail = 0
		self.stop_signal = task_lib.signaux.get_signum(in_config(self, params, "stopsignal")) or 15
		self.stoptime = in_config(self, params, "stoptime") or 10
		self.stop_timer = -1
		self.time = 0
		self.process = None

	def start(self, autostart):
		if (self.state ==  "NOT STARTING"):
			try:
				cmd_split = shlex.split(self.path)
				stdout_path = open(self.stdout, "a")
				stderr_path = open(self.stderr, "a")
				proc = subprocess.Popen(
					cmd_split,
					cwd = self.workingdir,
					stdin = subprocess.PIPE,
					stdout = stdout_path,
					stderr = stderr_path,
					env = os.environ
				)
				self.status = "STARTING"
				self.stop_timer = -1
				self.start_timer = 0
				self.process = proc
			except Exception, e:
				if (self.start_fail >= self.startretries):
					self.status = "FATAL"
				else:
					self.status = "FAILED"
				self.start_fail +=1
		else:
			self.status = "FATAL"

	def stop(self):
		self.process.send_signal(self.stop_signal)
		self.start_timer = -1
		self.start_fail = 0
		self.status = "STOPPING"
		self.stop_timer = 0

	def show_status(self):
		task_lib.line_format(self)

	def restart(self):
		self.stop()
		self.start(False)

	def finish(self, signum):
		self.start_timer = -1
		self.stop_timer = -1
		self.process = None
		self.status = "STOPPED"
		if (self.autorestart == True):
			self.start(False)
		elif (self.autorestart == "unexpected"):
			for exit in self.exit:
				if (exit == signum):
					self.start(False)
