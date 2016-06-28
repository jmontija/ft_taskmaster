import os
import stat
import time
import shlex
import subprocess
import task_lib

def check_validity(params, name):
	#"autorestart": str int
	type_define = {
		"cmd": str,
		"workingdir": str,
		"stopsignal": str,
		"stdout": str,
		"stderr": str,
		"numprocs": int,
		"autorestart": str,
		"autostart": bool,
		"exitcodes": list,
		"starttime": int,
		"startretries": int,
		"stoptime": int,
	}
	if (type(params[name]) is type_define[name]):
		print ("valid params ->" + name)
	else:
		print ("wrong params -> " + name)

	return (False)

def in_config(params, name):
	if (params):
		for k, v in params.iteritems():
			if (k == name and check_validity(params, name) == True):
				return (params[name])
	return None

class cmd_event:

	def __init__(self, key, params):
		self.id = key
		self.path = in_config(params, "cmd") or "ERROR"
		self.workingdir = in_config(params, "workingdir") or "/tmp"
		self.numprocs = in_config(params, "numprocs") or 1
		self.stdout = in_config(params, "stdout") or "/tmp/task_STDOUT"
		self.stderr = in_config(params, "stderr") or "/tmp/task_STDERR"
		self.autostart = in_config(params, "autostart")
		self.autorestart = in_config(params, "autorestart") or "unexpected"
		self.exit = in_config(params, "exitcodes") or [0, 2]
		self.starttime = in_config(params, "starttime") or 1
		self.start_timer = -1
		self.startretries = in_config(params, "startretries") or 1
		self.start_fail = 0
		self.stop_signal = task_lib.signaux.get_signum(in_config(params, "stopsignal")) or 15
		self.stoptime = in_config(params, "stoptime") or 10
		self.stop_timer = -1
		self.time = 0
		self.status = "WAITING"
		self.state = "NOT STARTING"
		self.process = None

	def start(self, autostart):
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
			self.start_timer = 0
			self.process = proc
		except Exception, e:
			if (self.start_fail >= self.startretries):
				self.status = "FATAL"
			else:
				self.status = "FAILED"
			self.start_fail +=1
			print("bad program -> " + self.id)

	def stop(self):
		self.start_fail = 0
		self.start_timer = -1
		self.process.send_signal(self.stop_signal)
		self.stop_timer = 0

	def show_status(self):
		if (self.process):
			print('{0:20}{1:15}{2:15}{3:15}{4:15}'.format(self.id, self.status, "  pid ", str(self.process.pid), "  uptime ", str(self.time)))
		else:
			print('{0:20}{1:15}{2:15}'.format(self.id, self.status, self.state))

	def restart(self):
		self.stop()
		self.start(False)

	def finish(self, signum):
		self.stop_timer = -1
		self.process = None
		self.status = "WAITING"
		self.show_status()
		if (self.autorestart == True):
			self.start(False)
		elif (self.autorestart == "unexpected"):
			for exit in self.exit:
				if (exit == signum):
					self.start(False)

class cmd_copy(cmd_event):

	def __init__(self, key, params):
		cmd_event.__init__(self, nom)



