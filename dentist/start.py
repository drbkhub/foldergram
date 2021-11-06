import time, subprocess, os
path = os.path.dirname(__file__)
task = subprocess.Popen([os.path.join(path, "start.exe")])
print('Начали')
time.sleep(10)
task.kill()