#!/usr/bin/env python
# encoding: utf-8
# @author: Krzysztof Królczyk (krzysztof.krolczyk@o2.pl)

from __future__ import print_function           # needed by ExternalCMD

import os                                       # needed by ExternalCMD
import sys                                      # needed by ExternalCMD
import shlex                                    # needed by ExternalCMD
import subprocess                               # needed by ExternalCMD

import requests                                 # for download_show_progress
from requests.exceptions import HTTPError       # for download_show_progress
from requests.exceptions import MissingSchema   # for download_show_progress
try:
    from requests.exceptions import ReadTimeout # for download_show_progress
except ImportError:
    from requests.exceptions import Timeout     # for download_show_progress

import contextlib                               # for temp_dir testing
import shutil                                   # for temp_dir testing
import tempfile                                 # for temp_dir testing

import logging


@contextlib.contextmanager
def cd(directory):
    old_dir = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(old_dir)

@contextlib.contextmanager
def temporary_dir(location=None, keep=False, overwrite=False):
    log = logging.getLogger(__file__)
    if overwrite and os.path.isdir(location):
        log.debug("Location cleanup, forced overwrite %s", location)
        shutil.rmtree(location)
    if location:
        assert not os.path.isdir(location)
        directory = os.makedirs(location)
        log.debug("makedir %s (OK)", directory)
    else:
        directory = tempfile.mkdtemp()
        log.debug("temp makedir %s (OK)", directory)
    yield directory
    if not keep:
        shutil.rmtree(directory)
        log.debug("directory cleanup %s (OK)", directory)

class open_ctx_cleanup(object):

    def __init__(self, path, mode):
        self.path = path
        self.mode = mode
        self._file_ = None

    def __enter__(self):
        self._file_ = open(self.path, self.mode)
        return self._file_

    def __exit__(self, exception_type, value, traceback):
        self._file_.close()
        if exception_type is not None:
            print (exception_type, value)
        os.remove(self._file_.name)

def get(url, timeout=None):
    try:
        info = {'url': url}
        response = requests.get(url, timeout=timeout, stream=True)
        info.update(response.headers)
        info.update({'status_code': response.status_code})
        return response, info
    except (MissingSchema, ReadTimeout) as err:
        raise ValueError(err)

def download_show_progress(url, save_location, timeout=None, progress=True):

    r = get(url)
    progress_bar_enabled = bool(progress)
    # In case progress was fptr callback:
    # prog_cb = progress
    progress = downloaded = chunks = 0
    chunk_size = 1024
    try:
        done = int(r[0].headers["content-length"])
        msg = '\rProgress: {} MB {}%  '
    except KeyError:
        progress_bar_enabled = False
    if not isinstance(save_location, file):
        print (save_location)
        save_location = open(save_location, 'wb')
    with save_location as file_:
        for chunk in r[0].iter_content(chunk_size):
            file_.write(chunk)
            downloaded += len(chunk)
            chunks += 1
            if progress_bar_enabled and (chunks & 5):
                # TODO: not thread safe.
                # Update every 5 chunks.
                progress = round((chunks / chunk_size), 2)
                prc = round((float(downloaded) / done) * 100, 2)
                # In case progress was fptr callback:
                #prog_cb(progress, prc)
                print(msg.format(progress, prc), end='')
    print ("\n")



class ExternalCMD(object):

    def __init__(self, cmd=None, chain_pipe={}, cwd=None,
                 quiet=False, pipe_in=None, parent=None):
        self.out = lambda: None
        self.quiet = quiet   # if not chain_pipe else False?
        self.cwd = cwd
        self.cmd = cmd
        self.pipe_in = pipe_in
        self.chain_pipe = chain_pipe
        self.parent = parent
        self.log = logging.getLogger(__file__)

    def _signal(self, signal):
        self.obj.send_signal(signal)

    def _kill(self):
        self.obj.kill()

    def run(self):
        kwargs = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if self.chain_pipe:
            kwargs.update(dict(stdin=subprocess.PIPE))
        if self.cwd:
            kwargs.update(dict(cwd=self.cwd))
        if self.pipe_in:
            kwargs.update(dict(stdin=self.pipe_in))
        try:
            obj = subprocess.Popen(shlex.split(self.cmd), **kwargs)
            if self.chain_pipe:
                self.chain_pipe.update({"pipe_in": obj.stdout, "parent": obj})
                nested = ExternalCMD(**self.chain_pipe)
            if self.parent:
                self.parent.stdout.close()
            if self.chain_pipe:
                # locals().update(nested.run())  # well, unpack dict to vars?
                # stdout_, stderr_, returncode = nested.run()
                results = nested.run()
                stdout_ = results["stdout_"]
                stderr_ = results["stderr_"]
                returncode_ = results["returncode_"]
            else:
                stdout_, stderr_ = obj.communicate(input=self.pipe_in)
                returncode_ = obj.returncode
            if not self.quiet:  # and not self.chain_pipe:
                # TODO (future): currently prevents reading
                # output if chained to other app, but
                # we should allow it anyway, by os.dup2(stdout_.fileno())
                # self.log.info (stdout_)
                # self.log.info (stderr_)
                print (stdout_)
                print (stderr_)
        except (Exception, subprocess.CalledProcessError) as err:
            self.log.critical(err)
            stdout_ = "Error: " + repr(err)
            stderr_ = ""
            raise
        finally:
            # dont try to encode empty '' string in py3
            # FIXME: probably better way to do it
            if not isinstance(stdout_, str):
                stdout_ = stdout_.decode(sys.stdout.encoding)
            if not isinstance(stderr_, str):
                stderr_ = stderr_.decode(sys.stdout.encoding)
        return dict(stdout_=stdout_, stderr_=stderr_, returncode_=returncode_)


def test_External_CMD_with_chained_grep():
    with temporary_dir(keep=False) as dir_:
        cmd_1 = "dmesg"
        cmd_2 = "grep usb"
        a = ExternalCMD(cmd=cmd_1,  # quiet=False,
                         chain_pipe={"cmd": cmd_2, "quiet": False})
        results = a.run()
        assert results["returncode_"] == 0
        assert os.path.isdir(dir_)
        assert len(results["stdout_"]) > 0


def test_External_CMD_with_chained_cmd():
    server = "http://download.opensuse.org"
    path = "/update/13.2/src/"
    filename = "IPython-2.2.0-2.5.1.src.rpm"
    url = "{}{}{}".format(server, path, filename)
    cmd_rpm = "rpm2cpio {}".format(url)
    cmd_cpio = "cpio -i --make-directories --verbose --unconditional"
    with open_ctx_cleanup("/tmp/tmp_rpm", 'wb') as tmp_file:
        download_show_progress(url, tmp_file)
        a = ExternalCMD(cmd=cmd_rpm,
                        chain_pipe={"cmd": cmd_cpio,
                                    "cwd": '/tmp',
                                    "quiet": True})
    results = a.run()


def test_requests_with_progress():
    url = "http://ipv4.download.thinkbroadband.com/100MB.zip"
    disk_loc = "/tmp/del_me"
    try:
        with open_ctx_cleanup(disk_loc, 'wb') as tmp_file:
            download_show_progress(url, tmp_file)
            try:
                with open(disk_loc, 'r') as test:
                    pass
            except Exception:
                assert False
    except KeyboardInterrupt:
        print ("Interrupted")


if __name__ == "__main__":
    test_requests_with_progress()
    test_External_CMD_with_chained_grep()
    test_External_CMD_with_chained_cmd()
