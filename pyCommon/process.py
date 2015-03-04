from threading import Thread
import os
import shlex
import logging
import platform
import subprocess

logger = logging.getLogger(__name__)

if platform.system() == 'Windows':
    import ctypes
    class disable_file_system_redirection:
        _disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
        _revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection
        def __enter__(self):
            self.old_value = ctypes.c_long()
            self.success = self._disable(ctypes.byref(self.old_value))
        def __exit__(self, type, value, traceback):
            if self.success:
                self._revert(self.old_value)

class ThreadCmd(Thread):
    def __init__(self, cmd, shell=False, disable_redirect=False, run_at=None, read_callback=None, realtime=False):
        Thread.__init__(self)
        self.cmd = cmd
        self.out = ""
        self.err = ""
        self.process = None
        self.shell = shell
        self.retcode = -1
        self.realtime = realtime
        self.run_at = run_at
        self.disable_redirect = disable_redirect
        self.started = False
        self.read_callback = read_callback
        if not read_callback:
            self.read_callback = self.append
    def append(self, stdout, stderr):
        self.out += stdout
        self.err += stderr
    def read(self, input=None):
        logger.debug("Communicate with %s" % self.process.pid)
        stdoutdata = ''
        stderrdata = ''
        if self.realtime:
            stdoutdata = self.process.stdout.readline()
        else:
            (stdoutdata, stderrdata) = self.process.communicate(input)
        self.read_callback(stdoutdata, stderrdata)
        logger.debug("Read %s" % stdoutdata)
        logger.debug("Error %s" % stderrdata)
    def run(self):
        old_path = os.getcwd()
        try:
            if self.run_at:
                os.chdir(self.run_at)
                logger.debug("Runing at %s" % self.run_at)
            args = shlex.split(self.cmd.encode('ascii'))
            self.process = None
            if platform.system() == 'Windows' and self.disable_redirect:
                with disable_file_system_redirection():
                    self.process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=self.shell)
            else:
                self.process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=self.shell)
            if self.run_at:
                os.chdir(old_path)

            logger.debug("Started proccess PID: %s (%s)" % (self.process.pid, args))
            while self.process.poll() is None:
                if self.read():
                    break
            self.retcode = self.process.returncode
        except Exception as ex:
            logger.exception(ex)
            logger.info("Error in: %s (%s)" %(self.cmd, ex))
            self.err += str(ex)
        finally:
            if old_path != os.getcwd():
                os.chdir(old_path)
        self.started = False
    def kill(self):
        self.started = False
        if self.process and self.process.poll() is None:
            self.process.terminate()
        if self.process and self.process.poll() is None:
            self.process.kill()
    def start(self):
        self.started = True
        Thread.start(self)
    def is_running(self):
        if self.process:
            return self.process.poll()
        return self.started
