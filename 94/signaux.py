# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    signaux.py                                         :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jmontija <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2016/06/30 10:05:29 by jmontija          #+#    #+#              #
#    Updated: 2016/06/30 10:05:30 by jmontija         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import signal
import task_lib

class siglib:

	def __init__(self):
		self.dico = signal.__dict__
		signal.signal(signal.SIGALRM, self.sig_alarm)
		signal.signal(signal.SIGINT, self.sig_int)
		signal.signal(signal.SIGCONT, self.sig_cont)
		signal.signal(signal.SIGQUIT, self.sig_quit)
		signal.alarm(1)

	def get_signum(self, name):
		if (name):
			for k, v in self.dico.iteritems():
				if k.startswith('SIG') and not k.startswith('SIG_') and k.endswith(name):
					return (v)
		return (0)

	def sig_quit(self ,signal, frame):
		task_lib.log.info('SIGQUIT has been called')
		pass

	def sig_cont(self ,signal, frame):
		task_lib.log.info('SIGCONT has been called')
		print ("A AJOUTER: la simulation control+D") ####

	def sig_int(self ,signal, frame):
		task_lib.log.info('SIGINT has been called')
		pass

	def sig_alarm(self, signum, frame):
		task = task_lib.task
		if (task):
			task.check_status()
		signal.alarm(1)
