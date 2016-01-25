# -*- coding: utf-8 -*-
import logging
from ConfigParser import ConfigParser, NoOptionError
import os, sys, time
import pexpect, pexpect.fdpexpect, threading, socket

# Btrfs / cp --reflink
#
# Potentially interesting QEMU options:
# -chroot dir     chroot to dir just before starting the VM
# -runas user     change to user id user just before starting the VM
# -snapshot       write to temporary files instead of disk image files
# -m megs         set virtual RAM size to megs MB [default=128]
# -mem-prealloc   preallocate guest memory (use with -mem-path)
# -g WxH[xDEPTH]  Set the initial graphical resolution and depth
# -vnc display    start a VNC server on display
# -monitor dev    redirect the monitor to char device 'dev'
# -qmp dev        like -monitor but opens in 'control' mode
# -mon chardev=[name][,mode=readline|control][,default]
# -debugcon dev   redirect the debug console to char device 'dev'
# -pidfile file   write PID to 'file'
# -no-reboot      exit instead of rebooting
# -no-shutdown    stop before shutdown
# -show-cursor    show cursor
# -loadvm [tag|id]
#                 start right away with a saved state (loadvm in monitor)
# -readconfig <file>
# -writeconfig <file>
#                 read/write config file
#  -snapshot - Temporary snapshot: write all changes to temporary files instead of hard drive image.

# -hda OVERLAY.img - Overlay snapshot: write all changes to an overlay image instead of hard drive image. The original image is kept unmodified. To create the overlay image:

# user $qemu-img create -f qcow2 -b ORIGINAL.img OVERLAY.img


class QEMUError(Exception):
	def __init__(self, value):
		self.value = value
	def __unicode__(self):
		return repr(self.value)
	def __str__(self):
		return unicode(self).encode('utf-8')


class QEMU:
	def __init__(self, conf_name, conf_file='qemu.ini'):
		'''	Starts a QEMU process with the specified configuration.
			It is expected that the format string used to start the process
			uses the 'wait' option for the monitor. This will require that
			someone connects to the QEMU monitor for the execution to start.
		'''
		# Initialize shared logger.
		QEMU.log = logging.getLogger(__name__)
		if not QEMU.log.handlers:
			# file logger
			f = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
			h1 = logging.FileHandler('%s.log' % (__name__))
			h1.setFormatter(f)
			QEMU.log.addHandler(h1)
			# stdout logger
			h2 = logging.StreamHandler(sys.stdout)
			h2.setFormatter(f)
			QEMU.log.addHandler(h2)
			# set loglevel
			QEMU.log.setLevel(logging.DEBUG)
			QEMU.log.info('Logger started.')

		# Read configuration file.
		self.conf_parser = ConfigParser()
		self.conf_file = conf_file
		self.conf_name = conf_name
		self.conf_parser.readfp(open(self.conf_file))

		# Get configuration values.
		self.qemu_cmd_fmt = self.conf_parser.get('qemu-controller', 'qemu_cmd_fmt')
		self.qemu_monhost = self.conf_parser.get('qemu-controller', 'qemu_monhost')
		self.qemu_monport = self.conf_parser.getint('qemu-controller', 'qemu_monport')
		self.qemu_vnchost = self.conf_parser.get('qemu-controller', 'qemu_vnchost')
		self.qemu_vncport = self.conf_parser.getint('qemu-controller', 'qemu_vncport')
		self.conf = dict(self.conf_parser.items(self.conf_name))
		required = ['qemu', 'qcow_dir', 'vmhda', 'vmram']
		missing = [opt for opt in required if not opt in self.conf]
		if missing:
			raise NoOptionError(missing, self.conf_name)

		# Fix-up configuration values.
		path_expand = lambda s: os.path.expandvars(os.path.expanduser(s))
		self.conf['qemu'] = path_expand(self.conf['qemu'])
		self.conf['qcow_dir'] = path_expand(self.conf['qcow_dir'])
		self.conf['vmhda'] = os.path.join(self.conf['qcow_dir'], self.conf['vmhda'])
		self.conf['vmram'] = int(self.conf['vmram'])
		self.conf['vmname'] = self.conf_name
		self.conf['vmmonhost'] = self.qemu_monhost
		self.conf['vmmonport'] = self.qemu_monport
		self.conf['vmvnchost'] = self.qemu_vnchost
		self.conf['vmvncport'] = self.qemu_vncport

		# Initialized other values.
		self.qemu_process = None
		self.qemu_monitor = None
		self.qemu_thread = threading.Thread(target=self.__qemu_runner)
		self.qemu_thread.start()

		# print self.conf


	def __qemu_runner(self):
		'''	Thread wrapping the QEMU process.
			We don't interact with the process directly.
			All interactions happen through the QEMU monitor.
		'''
		# Start process and wait for connection prompt.
		qemu_process = pexpect.spawn(self.qemu_cmd_fmt.format(**self.conf))
		try:
			r = qemu_process.expect('QEMU waiting for connection', timeout=3)
			QEMU.log.info('QEMU started. Monitor on {vmmonhost}:{vmmonport}.'.format(**self.conf))
			self.qemu_process = qemu_process
			self.qemu_process.interact()
			QEMU.log.info('QEMU finished.')
		except pexpect.TIMEOUT:
			QEMU.log.error('QEMU failed to start (?).')


	def start(self):
		'''	Connects to QEMU monitor, which triggers the start of the execution.
		'''
		if self.qemu_monitor:
			QEMU.log.info('QEMU already started. Monitor on {vmmonhost}:{vmmonport}.'.format(**self.conf))
			return
		if not self.qemu_process:
			# No process yet. Wait a few secs.
			QEMU.log.info('Waiting for QEMU monitor...')
			time.sleep(3)
		try:
			ctuple = (self.conf['vmmonhost'], self.conf['vmmonport'])
			self.qemu_monitor = socket.socket()
			self.qemu_monitor.connect(ctuple)
			QEMU.log.info('Go')
			self.qemu_monitor.close()
		except:
			QEMU.log.error('Could not connect to QEMU monitor on {vmmonhost}:{vmmonport}.'.format(**self.conf))
			raise

	def kill(self):
		'''Terminates the QEMU process.
		'''
		self.qemu_process.terminate()

	def raw_command(self, cmd):
		pass


class PANDA(QEMU):
	trace_file = None

	def begin_record(self, trace_file=None):
		pass

	def end_record(self):
		pass

	def is_recording(self):
		return False if trace_file is None else True