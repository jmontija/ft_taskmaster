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

dup = copy.deepcopy
signaux = siglib()
task = task_event()
