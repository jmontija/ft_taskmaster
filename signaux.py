import signal
import cmd_info

class siglib:

	def __init__(self):
		self.dico = signal.__dict__
		signal.signal(signal.SIGALRM, self.sig_alarm)
		signal.signal(signal.SIGINT, self.sig_int)
		signal.alarm(7)

	def get_signum(self, name):
		if (name):
			for k, v in self.dico.iteritems():
				if k.startswith('SIG') and not k.startswith('SIG_') and k.endswith(name):
					return (v)
		elif (name == None):
			return (15)
		return (0)

	def sig_int(self ,signal, frame):
		pass

	def sig_alarm(self, signum, frame):
		task = cmd_info.task
		if (task):
			task.check_status()
		signal.alarm(1)