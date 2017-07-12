from distutils.core import setup
import py2exe
import glob

excludes = [
	"pywin" ,
	"pywin debugger" ,
	"pywin debugger.dbgcon" ,
	"pywin dialogs" ,
	"pywin dialogs.list" ,
	"win32com.server" ,
]

options = {
	"bundle_files" : 1,
	"compressed" : 1,
	"excludes" : excludes,
	"dll_excludes" : ["w9xpopen" , "MSVCP90.dll"]
}

setup(
	options = {"py2exe" : options},
	zipfile = None,
	console = ["JELLYFISHING.py"],
	#windows = [""]
	data_files=[("images", glob.glob("images/*"))]

)
