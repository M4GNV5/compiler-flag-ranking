import os, re, tempfile

reg = re.compile("(?<!\w)--?[a-zA-Z0-9-_]+")

fd = tempfile.NamedTemporaryFile(mode="r+", encoding="utf8", prefix="gcc-man")
os.system("man gcc > " + fd.name)
gccMan = fd.read()

options = reg.findall(gccMan)
options = list(set(options))

with open("gcc-options.list", "w+") as fout:
	for opt in options[:-1]:
		fout.write(opt)
		fout.write("\n")

	fout.write(options[-1])
