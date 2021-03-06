import sublime
import sublime_plugin
import threading
from ..utils import *

class JavatarInstallCommand(sublime_plugin.WindowCommand):
	def run(self, installtype=None, name=None, filename=None, url=None, checksum=None):
		if installtype is not None:
			if installtype == "remote_package":
				thread = JavatarRemotePackageInstallerThread(name, filename, url, checksum, self.on_complete)
				thread.start()
				ThreadProgress(thread, "Installing Javatar package \"" + name + "\"", "Javatar package \"" + name + "\" has been successfully installed")

	def on_complete(self):
		resetPackages()
		loadPackages()

class JavatarRemotePackageInstallerThread(threading.Thread):
	def __init__(self, name, filename, url, checksum, on_complete=None):
		self.pckname = name
		self.filename = filename
		self.url = url
		self.checksum = checksum
		self.on_complete = on_complete
		threading.Thread.__init__(self)

	def run(self):
		try:
			self.result_message = "Javatar package \"" + self.pckname + "\" has been corrupted"
			urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler()))
			data = urllib.request.urlopen(self.url+self.filename+".javatar-packages").read()
			datahash = hashlib.sha256(data).hexdigest()
			if self.checksum != datahash:
				self.result = False
				return
			open(getPath("join", getPath("join", sublime.packages_path(), "user"), self.filename+".javatar-packages"), "wb").write(data)
			self.result = True
			if self.on_complete is not None:
				sublime.set_timeout(self.on_complete, 10)
		except Exception as e:
			self.result_message = "Javatar package \"" + self.pckname + "\" installation has failed: "+ str(e)
			self.result = False
