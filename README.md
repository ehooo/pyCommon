# Licence
Copyright (C) 2015 [ehooo](https://github.com/ehooo)

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# About:
Collection of usefull class, functions and tools

# pyCommon.process
Content a class ThreadCmd, for run command win32/win64 and unix
```
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
```

# pyCommon.network
Colleciton of functions for donwload and upload from internet
```
from pyCommon.network import *
import sys

wget = WGet()
wget.web("https://raw.githubusercontent.com/ehooo/pyCommon/master/LICENSE")
wget.save_file = 'LICENSE.txt'
wget.donwload(update_callback=wget.save_callback)
print wget._tmp_file

filepath = sys.args[0]
wget.web("http://example.com/upload")
print wget.upload(filepath)
```
