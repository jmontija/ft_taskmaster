# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    cmd_event.py                                       :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jmontija <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2016/06/30 10:04:58 by jmontija          #+#    #+#              #
#    Updated: 2016/06/30 10:05:00 by jmontija         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import time
import shlex
import subprocess
import task_lib
import cmd_lib

class cmd_event:

	def __init__(self, key, params):

		in_config = cmd_lib.in_config

		self.id = key
		self.status = "WAITING"
		self.state = "OK"
		self.path = in_config(self, params, "cmd") or task_lib.color_string("RED","Empty")
		self.workingdir = in_config(self, params, "workingdir") or "/tmp"
		self.numprocs = in_config(self, params, "numprocs") or 1
		self.stdout = in_config(self, params, "stdout") or "/tmp/task_STDOUT"
		self.fdout = None
		self.stderr = in_config(self, params, "stderr") or "/tmp/task_STDERR"
		self.fderr = None
		self.autostart = in_config(self, params, "autostart") or False
		self.autorestart = in_config(self, params, "autorestart") or False
		self.exit = in_config(self, params, "exitcodes") or [0, 2]
		self.starttime = in_config(self, params, "starttime") or 1
		self.start_timer = -1
		self.startretries = in_config(self, params, "startretries") or 3
		self.start_fail = 0
		self.stop_signal = task_lib.signaux.get_signum(in_config(self, params, "stopsignal")) or 15
		self.stoptime = in_config(self, params, "stoptime") or 1
		self.umask = in_config(self, params, "umask") or 022
		self.stop_timer = -1
		self.time = 0
		self.process = None
		self.env = task_lib.set_env(os.environ, in_config(self, params, "env"))

		if (self.state == "OK"): cmd_lib.post_init(self)
		if (self.state != "OK"):
			self.status = "FATAL"
		task_lib.log.info(self.id + ': has been created: status:' + self.status)

	def start(self, autostart):
		if (self.state ==  "OK" or self.state == "ERROR processus: check: /tmp/logger.task"):
			try:
				cmd_split = shlex.split(self.path)
				proc = subprocess.Popen(
					cmd_split,
					cwd = self.workingdir,
					stdin = subprocess.PIPE,
					stdout = self.fdout,
					stderr = self.fderr,
					env = self.env
				)
				self.status = "STARTING"
				self.stop_timer = -1
				self.start_timer = 0
				self.process = proc
				self.time = time.time()
				task_lib.log.info(self.id + ': is starting: status:' + self.status)
			except Exception, e:
				if (self.start_fail >= self.startretries):
					self.status = "FATAL"
				else:
					self.status = "FAILED"
					self.state = "ERROR processus: check: /tmp/logger.task"
					task_lib.log.warning(self.id + ': ' + e.strerror)
				self.start_fail +=1
		else:
			self.status = "FATAL"

	def stop(self):
		self.start_timer = -1
		self.start_fail = 0
		self.stop_timer = 0
		self.status = "STOPPING"
		task_lib.log.info(self.id + ': is stopping: status:' + self.status)
		try:
			self.process.send_signal(self.stop_signal)
		except OSError, e:
			task_lib.log.warning(self.id + ': ' + e.strerror)
			self.finish(15)

	def show_status(self):
		task_lib.line_format(self)


	def restart(self):
		task_lib.log.info(self.id + ': is restarting: status:' + self.status)
		self.stop()
		self.start(False)

	def finish(self, signum):
		self.start_timer = -1
		self.stop_timer = -1
		self.status = "STOPPED"
		self.process = None
		task_lib.log.info(self.id + ': has been stopped: status:' + self.status)
		if (self.autorestart == True):
			self.start(False)
		elif (self.autorestart == "unexpected"):
			for exit in self.exit:
				if (exit == signum):
					self.start(False)
