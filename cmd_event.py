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
		self.numprocs = in_config(self, params, "numprocs") or 1 #0
		self.stdout = in_config(self, params, "stdout") or "/tmp/task_STDOUT"
		self.fdout = None
		self.stderr = in_config(self, params, "stderr") or "/tmp/task_STDERR"
		self.fderr = None
		self.autostart = in_config(self, params, "autostart") or False
		self.autorestart = in_config(self, params, "autorestart") or task_lib.color_string("RED","unexpected")
		self.exit = in_config(self, params, "exitcodes") or [0, 2]
		self.starttime = in_config(self, params, "starttime") or 1
		self.start_timer = -1
		self.startretries = in_config(self, params, "startretries") or 3
		self.start_fail = 0
		self.stop_signal = task_lib.signaux.get_signum(in_config(self, params, "stopsignal")) or 15
		self.stoptime = in_config(self, params, "stoptime") or 10
		self.umask = in_config(self, params, "umask") or 644
		self.stop_timer = -1
		self.time = 0
		self.process = None
		self.env = task_lib.set_env(os.environ, in_config(self, params, "env"))

		if (self.state == "OK"): cmd_lib.post_init(self)
		if (self.state != "OK"):
			self.status = "FATAL"
		task_lib.log.info(self.id + ': has been created: status:' + self.status)

	def show_status(self):
		task_lib.line_format(self)

	def print_all_info(self, line):
		try:
			timer = time.time()
			time_delta = time.gmtime(timer - self.time)
			curr_time = time.strftime("%H:%M:%S", time_delta)
			print ("_"*35 + " < " + line + " > " + "_"*35)
			print(  "Status:              " + task_lib.format_statut(self.status))
			print(	"State:               " + str(self.state))
			print(	"Path:                " + str(self.path))
			print(	"workingdir:          " + str(self.workingdir))
			print(	"Numprocs:            " + str(self.numprocs))
			print(	"Stdout:              " + str(self.stdout))
			print(	"Stderr:              " + str(self.stderr))
			print(	"Autostart:           " + str(self.autostart))
			print(	"Autorestart:         " + str(self.autorestart))
			print(	"Exit codes:          " + str(self.exit))
			print(	"Stop signal:         " + str(self.stop_signal))
			print(	"Start fail | retry:  " + str(self.start_fail) + " | " +str(self.startretries))
			print(	"Stop time:           " + str(self.stoptime) )
			if (self.process != None):
				print ("_PROCESS_INFO" + "_"*((70-13 + len(line))/2))
				print ("PID:            " + str(self.process.pid))
				print ("Process stdin:  " + str(self.process.stdin))
				print ("Process stdout: " + str(self.process.stdout))
				print ("Process stderr: " + str(self.process.stderr))
				print ("time:           " + str(curr_time))

		except:
			print ("Info: " + line + ": Failed (INFOERR)")

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
					env = os.environ
				)
				self.status = "STARTING"
				self.state =  "OK"
				self.start_fail = 0
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
					self.state = task_lib.color_string("RED", "ERROR processus: check: /tmp/logger.task")
					task_lib.log.warning(self.id + ': ' + e.strerror)
				self.start_fail += 1
		else:
			self.status = "FATAL"

	def stop(self):
		self.process.send_signal(self.stop_signal)
		self.start_timer = -1
		self.start_fail = 0
		self.status = "STOPPING"
		self.stop_timer = 0
		task_lib.log.info(self.id + ': is stopping: status:' + self.status)


	def restart(self):
		task_lib.log.info(self.id + ': is restarting: status:' + self.status)
		self.stop()
		self.start(False)

	def finish(self, signum):
		self.start_timer = -1
		self.stop_timer = -1
		self.process = None
		self.status = "STOPPED"
		task_lib.log.info(self.id + ': has been stopped: status:' + self.status)
		if (self.autorestart == True):
			self.start(False)
		elif (self.autorestart == "unexpected"):
			for exit in self.exit:
				if (exit == signum):
					self.start(False)
