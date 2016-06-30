# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    task_lib.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jmontija <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2016/06/30 10:05:49 by jmontija          #+#    #+#              #
#    Updated: 2016/06/30 10:05:50 by jmontija         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import copy
import yaml
import time
import logging
from signaux import siglib
from task_event import task_event

dup = copy.deepcopy
log = logging
log.basicConfig(filename = '/tmp/logger.task', level=logging.DEBUG)

def color_string(line, s):
	color_define = {
		"BOLD": "\033[1m" + s + "\033[0m" + "\033[39m",
		"RED": "\033[31m" + s +  "\033[39m",
		"GREEN": "\033[32m" + s + "\033[39m",
		"YELLOW": "\033[33m" + s + "\033[39m",
		"BLUE": "\033[34m" + s + "\033[39m",
		"MAGENTA": "\033[35m" + s + "\033[39m",
		"CYAN": "\033[36m" + s + "\033[39m",
		"BACK_YEL" : "\033[43m" + "\033[1m" "\033[30m" + s + "\033[0m" + "\033[39m" + "\t   ",
		"BACK_RED": "\033[41m" + "\033[1m" + s + "\033[0m" + "\033[39m" + "\t   ",
		"DEFAULT" : "\033[0m" + "\033[39m" + s,
	}
	return str(color_define[line])

def format_statut(line):
	color_match = {
		"WAITING": "DEFAULT",
		"STARTING": "CYAN",
		"RUNNING": "GREEN",
		"STOPPING": "MAGENTA",
		"BROKEN": "YELLOW",
		"STOPPED": "RED",
		"FAILED": "BACK_YEL",
		"FATAL": "BACK_RED",
	}
	return color_string(color_match[line], line + " "*(8 - len(line)))

def line_format(self): ####
	timer = time.time()
	time_delta = time.gmtime(timer - self.time)
	curr_time = time.strftime("uptime: %H:%M:%S", time_delta)
	if (self.process):
		print('{0:37}{1:28}{2:15}{3:23}{4:15}'.format( \
					color_string("BOLD", self.id), \
					format_statut(self.status), \
					"  pid ", \
					color_string("BOLD", str(self.process.pid)), \
					str(curr_time)))
	else:
		print('{0:24}{1:28}{2:15}'\
			.format(self.id, \
				format_statut(str(self.status)), \
				str(self.state)))

def load_conf(file):
	try:
		fd = open(file, "r")
		data = yaml.load(fd)
		fd.close()
		return data
	except Exception, e:
		print("ERROR loading yaml's data -> check yourfile.yaml")
		log.warning("ERROR loading yaml's data -> check yourfile.yaml")

def check_process(cmd, line):
	for k, v in cmd.iteritems():
		curr = cmd[k]
		if (curr.process and curr.id == str(line)):
			return (curr)
	return (None)

def close_fd(all_cmd):
	for k, v in all_cmd.iteritems():
		cmd = all_cmd[k]
		try:
			os.close(cmd.fdout)
		except:
			pass
		try:
			os.close(cmd.fderr)
		except:
			pass

def set_env(environ_os, environ_user):
	try:
		final_environ =  copy.deepcopy(environ_os)
		final_environ.update(environ_user)
		return final_environ
	except:
		print ("set_env: Err")
		log.warning("ERROR Environnement")

signaux = siglib()
task = task_event()
