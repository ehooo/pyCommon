from pyCommon.process import ThreadCmd
import sys


def callback(stdout, stderr):
    sys.stdout.write(stdout)
    sys.stderr.write(stderr)


cmd = ThreadCmd("pwd", run_at="/etc/", read_callback=callback, realtime=True)
cmd.start()
while cmd.is_running():
    cmd.join(1)
cmd = ThreadCmd("pwd", run_at="/home/")
cmd.start()
cmd.join(10)
if not cmd.is_running():
    cmd.kill()
sys.stdout.write(cmd.out)
sys.stderr.write(cmd.err)

wget = WGet()
wget.web("https://raw.githubusercontent.com/ehooo/pyCommon/master/LICENSE")
wget.save_file = 'LICENSE.txt'
wget.donwload(update_callback=wget.save_callback)
print wget._tmp_file

filepath = sys.args[0]
wget.web("http://example.com/upload")
print wget.upload(filepath)
