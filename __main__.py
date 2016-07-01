# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    __main__.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jmontija <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2016/06/30 10:04:15 by jmontija          #+#    #+#              #
#    Updated: 2016/06/30 10:04:20 by jmontija         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #
import signal
import cmd
import os
import subprocess
from task_lib import task
from task_lib import close_fd
from task_lib import log

def opening():
    try:
        fd = open("opening.master", "r")
        print fd.read()
        fd.close()
    except:
        print ("opening failed___\n\n")
    log.info("TASK_MASTER LAUNCH:")


class keyboard(cmd.Cmd):
    prompt = '\033[31m' + '\033[1m' + '(Deamon_Master): ' + '\033[39m' + '\033[0m'

    def emptyline(self):
        pass

    def do_info(self, line):
        task.info(line)

    def do_status(self, line):
        task.status(line)

    def do_start(self, line):
        task.start(line)

    def do_stop(self, line):
        if (line != ""):
            task.stop(line)
        else:
            print("task: need name to stop")

    def do_shell(self, line):
        proc = subprocess.Popen(
                line,
                shell = True,
                env = os.environ
        )
        proc.wait()

    def do_restart(self, line):
        task.restart(line)

    def do_reload(self, line):
        task.reload()

    def do_only(self, line):
        task.only(line)

    def do_help(self, line):
        print ("cmd: <info/status/start/stop/restart> [all/name] || <reload/quit> ")

    def do_quit(self, line):
        signal.alarm(0)
        close_fd(task.cmd)
        task.stop("all")
        print ("see you soon on 'Deamon_Master' .\nclosing ...")
        log.info("TASK_MASTER CLOSED!")
        return True

    def do_EOF(self, line):
        self.do_quit(line)
        return True

if __name__ == "__main__":
    opening()
    task.autostart()
    task.status("")
    keyboard().cmdloop()
