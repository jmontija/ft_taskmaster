import copy
import yaml
from signaux import siglib
from task_event import task_event

def load_conf(file):
	try:
		fd = open(file, "r")
		data = yaml.load(fd)
		fd.close()
		return data
	except Exception, e:
		print("error config -> " + file)

def check_process(cmd, line):
	for k, v in cmd.iteritems():
		curr = cmd[k]
		if (curr.process and curr.id == str(line)):
			return (curr)
	return (None)

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

def line_format(self):
	if (self.process):
		print('{0:37}{1:27}{2:15}{3:23}{4:15}'.format( \
					color_string("BOLD", self.id), \
					format_statut(self.status), \
					"  pid ", \
					color_string("BOLD", str(self.process.pid)), \
					"  uptime ",\
				 	str(self.time)))
	else:
		print('{0:24}{1:27}{2:15}'\
			.format(self.id, \
				format_statut(str(self.status)), \
				str(self.state)))


def set_env(environ_os, environ_user):
	try:
		final_environ =  copy.deepcopy(environ_os)
		final_environ.update(environ_user)
		return final_environ
	except:
		print ("set_env: Err")

dup = copy.deepcopy
signaux = siglib()
task = task_event()
