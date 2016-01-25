# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
import os
import pexpect

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


class QEMUError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class QEMUConfError(Exception):
	pass

class QEMU:
	def __init__(self, conf_name, conf_file='qemu.ini'):
		# Get configuration items.
		self.conf_parser = ConfigParser()
		self.conf_file = conf_file
		self.conf_name = conf_name
		try:
			self.conf_parser.readfp(open(self.conf_file))
		except:
			raise QEMUConfError("Can't read config file '%s'." % (self.conf_file))
		if not self.conf_parser.has_section(self.conf_name):
			raise QEMUConfError("Can't read config '%s' from file '%s'." % (
				self.conf_name, self.conf_file
			))
		self.conf = dict(self.conf_parser.items(self.conf_name))

		# Check required items.
		required = ['qemu', 'qcow_dir', 'vmhda', 'vmram']
		missing = [i for i in required if not i in self.conf]
		if missing:
			raise QEMUConfError("Can't find required option%s %s in config '%s' of file '%s'." % (
				's' if len(missing)>1 else '', missing, self.conf_name, self.conf_file
			))

		# Fix-up configuration values.
		path_expand = lambda s: os.path.expandvars(os.path.expanduser(s))
		self.conf['qemu'] = path_expand(self.conf['qemu'])
		self.conf['qcow_dir'] = path_expand(self.conf['qcow_dir'])
		self.conf['vmhda'] = os.path.join(self.conf['qcow_dir'], self.conf['vmhda'])
		self.conf['vmram'] = int(self.conf['vmram'])

		print self.conf

		# ./i386-softmmu/qemu-system-i386 -m 256 -hda ../../pandavm/debian.qcow2 -vnc :0 -monitor telnet:127.0.0.1:1234,server


		qemu_cmd_fmt = '{qemu} -display vnc=:0 -m {vmram} -name lolo -mem-prealloc -hda {vmhda}'
		print qemu_cmd_fmt.format(**self.conf)
		self.monitor = pexpect.spawn(qemu_cmd_fmt.format(**self.conf))

		# print self.qemu, self.vmhda, self.vmram


	def start(self):
		pass

	def kill(self):
		'''Terminates this QEMU instance.
		'''
		pass


class PANDA(QEMU):
	trace_file = None

	def begin_record(self, trace_file=None):
		pass

	def end_record(self):
		pass

	def is_recording(self):
		return False if trace_file is None else True