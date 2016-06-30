# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    cmd_lib.py                                         :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jmontija <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2016/06/30 10:05:09 by jmontija          #+#    #+#              #
#    Updated: 2016/06/30 10:05:16 by jmontija         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import task_lib

def	post_init(cmd):

	# OVER
	if (cmd.umask > 7777):
		cmd.state = "ERROR -> umask"
		task_lib.log.warning(cmd.id + ': ' + cmd.state)
	if (cmd.numprocs > 5000):
		cmd.state = "ERROR -> too many processus"
		task_lib.log.warning(cmd.id + ': ' + cmd.state)
	if (cmd.workingdir[0] != "/" or os.access(cmd.workingdir, os.W_OK) == False):
		cmd.state = "ERROR -> wrong path"
		task_lib.log.warning(cmd.id + ': ' + cmd.state)
	if (cmd.stop_signal < 0 or cmd.stop_signal > 30):
		cmd.state = "ERROR -> signaux"
		task_lib.log.warning(cmd.id + ': ' + cmd.state)

	# OPEN
	if (cmd.state == "OK"):
		try:
			cmd.fdout = os.open(cmd.stdout, os.O_WRONLY | os.O_CREAT, cmd.umask)
		except OSError, e:
			cmd.state = "ERROR opening -> " + e.filename
			task_lib.log.warning(cmd.id + ': ' + cmd.state)
			cmd.fdout = None
		try:
			cmd.fderr = os.open(cmd.stderr, os.O_WRONLY | os.O_CREAT, cmd.umask)
		except OSError, e:
			cmd.state = "ERROR opening -> " + e.filename
			task_lib.log.warning(cmd.id + ': ' + cmd.state)
			cmd.fderr = None

	#CHECK_PATH
	if (cmd.path[0] == '.' or cmd.path[0] == '/'):
		if os.access(cmd.path, os.X_OK) == False:
			cmd.state = "ERROR -> command"
			task_lib.log.warning(cmd.id + ': ' + cmd.state)
	else:
		find = False
		path_env = os.environ["PATH"]
		path_env = path_env.split(":")
		curr_cmd = cmd.path.split()[0]
		for path in path_env:
			curr_path = path + "/" + curr_cmd
			if os.access(curr_path, os.X_OK) == True:
				find = True
				break
		if (find == False):
			cmd.state = "ERROR -> command"
			task_lib.log.warning(cmd.id + ': ' + cmd.state)


def special_params(cmd, params, name):
	if (name == "autorestart"):
		if ((type(params[name]) is int and params[name] < 0) or params[name] != "unexpected"):
			cmd.state = "ERROR -> " + name
			task_lib.log.warning(cmd.id + ': ' + cmd.state)
			return (False)
	elif (name == "exitcodes"):
		if (type(params[name]) is not list):
			return (False)
		for exit in params[name]:
			if ((type(exit) is int and exit < 0) or type(exit) is not int):
				cmd.state = "ERROR -> " + name
				task_lib.log.warning(cmd.id + ': ' + cmd.state)
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
		"umask": int,
		"env": dict,
	}
	if (name == "autorestart" or name == "exitcodes"):
		return (special_params(cmd, params, name))
	elif (type(params[name]) is type_define[name]):
		if (type_define[name] is int and params[name] < 0):
			cmd.state = "ERROR -> " + name
			task_lib.log.warning(cmd.id + ': ' + cmd.state)
			return (False)
	elif (type(params[name]) is not type_define[name]):
		cmd.state = "ERROR -> " + name
		task_lib.log.warning(cmd.id + ': ' + cmd.state)
		return (False)
	return (True)

def in_config(cmd, params, name):
	if (params):
		for k, v in params.iteritems():
			if (k == name and check_validity(cmd, params, name) == True):
				return (params[name])
	return None
