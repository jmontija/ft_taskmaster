import cmd
from task_lib import task

def opening():
    try:
        fd = open("opening.master", "r")
        print fd.read()
    except:
        print ("opening failed___\n\n")

class keyboard(cmd.Cmd):
    prompt = '\033[31m' + '\033[1m' + '(Deamon_Master): ' + '\033[39m' + '\033[0m'

    def emptyline(self):
    	pass

    def do_status(self, line):
    	task.status(line)

    def do_start(self, line):
    	task.start(line)

    def do_stop(self, line):
    	if (line != ""):
    		task.stop(line)
    	else:
    		print("task: need PID to stop")

    def do_restart(self, line):
    	task.restart(line)

    def do_reload(self, line):
        task.reload()

    def do_help(self, line):
    	print ("cmd: <status/start/stop/restart> [all/name/pid] || <reload/quit> ")

    def do_quit(self, line):
        return True

if __name__ == "__main__":
    opening()
    task.autostart()
    task.status("")
    keyboard().cmdloop()
