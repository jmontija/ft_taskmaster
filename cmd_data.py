import os
import time
import shlex
import subprocess
import cmd_info

def in_config(params, name):
	if (params):
		for k, v in params.iteritems():
			if (k == name):
				return (params[k])
	return None

class cmd_data:

	def __init__(self, key, params):
		self.id = key
		self.path = in_config(params, "cmd") or "ls -R /Applications"
		self.workingdir = in_config(params, "workingdir") or "/tmp"
		self.numprocs = in_config(params, "numprocs") or 1
		self.stdout = in_config(params, "stdout") or "/tmp/task_STDOUT"
		self.stderr = in_config(params, "stderr") or "/tmp/task_STDERR"
		self.autostart = in_config(params, "autostart") or False
		self.autorestart = in_config(params, "autorestart") or "unexpected"
		self.exit = in_config(params, "exitcodes") or [0, 2]
		self.starttime = in_config(params, "starttime") or 1
		self.start_timer = -1
		self.startretries = in_config(params, "startretries") or 1
		self.start_fail = 0
		self.stop_signal = cmd_info.signaux.get_signum(in_config(params, "stopsignal")) or 15
		self.stoptime = in_config(params, "stoptime") or 10
		self.stop_timer = -1
		self.time = 0
		self.status = "WAITING"
		self.process = None

	def start(self, autostart):
		try:
			#time.sleep(self.starttime)
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
			self.start_timer = 0
			self.status = "RUNNING"
			if (autostart == False):
				self.show_status()
			self.process = proc
		except Exception, e:
			print("bad program -> " + self.id)

	def stop(self):
		self.process.send_signal(self.stop_signal)
		self.stop_timer = 0

	def show_status(self):
		if (self.process):
			print('{0:20}{1:15}{2:15}{3:15}{4:15}'.format(self.id, self.status, "  pid ", str(self.process.pid), "  uptime ", str(self.time)))
		else:
			print('{0:20}{1:15}{2:15}{3:15}{4:15}'.format(self.id, self.status, "  pid ", '0', "  uptime ", str(self.time)))

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



