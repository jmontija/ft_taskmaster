import cmd
from cmd_info import task

class HelloWorld(cmd.Cmd):

    prompt = 'task MASTER: '

    def emptyline(self):
    	pass

    def do_status(self, line):
    	task.status()

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
    	print("reload: " + line)

    def do_help(self, line):
    	print ("cmd: <status/start/stop/restart> [all/name/pid] || <reload/quit> ")

    def do_quit(self, line):
        return True

if __name__ == "__main__":
	task.autostart()
	task.status()
	HelloWorld().cmdloop()
