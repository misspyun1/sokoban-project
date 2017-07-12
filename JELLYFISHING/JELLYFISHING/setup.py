from distutils.core import setup
import py2exe,sys,os
includes=["encodings","encodings.utf_8",]
options={
	"bundle_files" : 1,
	"compressed" :1,
	"optimize" :2,
        "includes":includees,}
setup(console=[{'script':"JELLYFISHING.py"}],
      options={"py2exe":options},
      zipfile=None,)
