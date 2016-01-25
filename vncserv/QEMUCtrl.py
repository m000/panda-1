# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser, NoOptionError
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
		# Read configuration file.
		self.conf_parser = ConfigParser()
		self.conf_file = conf_file
		self.conf_name = conf_name
		self.conf_parser.readfp(open(self.conf_file))

		# Get configuration values.
		self.qemu_cmd_fmt = self.conf_parser.get('qemu-controller', 'qemu_cmd_fmt')
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

		print self.conf
		print self.qemu_cmd_fmt.format(**self.conf)
		# self.monitor = pexpect.spawn(qemu_cmd_fmt.format(**self.conf))

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