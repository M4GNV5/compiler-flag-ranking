import os, sys, requests, concurrent.futures

def apiRequest(repo, path):
	url = "https://api.github.com/repos/{}{}".format(repo, path)
	headers = {"Authorization": "token {}".format(githubToken)}
	res = requests.get(url, headers=headers)
	if res.status_code != 200:
		raise Exception("Received {}: {}".format(res.status_code, res.text))

	return res.json()

def checkFile(repo, path, flags):
	url = "https://raw.githubusercontent.com/{}/master/{}".format(repo, path)
	res = requests.get(url)
	if res.status_code == 404:
		return
	elif res.status_code != 200:
		print("Received {}: {}".format(res.status_code, res.text), file=sys.stderr)
		exit(1)

	filePath = os.path.join("repos", repo, path)
	folderPath = os.path.dirname(filePath)
	os.makedirs(folderPath, exist_ok=True)
	with open(filePath, "w+") as fd:
		fd.write(res.text)

	for flag in compilerFlags:
		if flag in res.text:
			flags.add(flag)

def checkRepo(repo):
	print("[{}] checking...".format(repo), file=sys.stderr)

	flags = set()
	commits = apiRequest(repo, "/commits")
	tree = apiRequest(repo, "/git/trees/{}?recursive=true".format(commits[0]["sha"]))

	fileCount = 0
	for node in tree["tree"]:
		if node["type"] == "blob":
			path = node["path"]
			for name in buildFileNames:
				if path.endswith(name):
					checkFile(repo, path, flags)
					fileCount += 1

			if fileCount >= 1024:
				break

	print("[{}] found {} distinct flags in {} build files".format(repo, len(flags), fileCount), file=sys.stderr)

	with open(os.path.join("output", repo.replace("/", "_")), "w+") as fd:
		for flag in flags:
			fd.write(flag)
			fd.write("\n")

buildFileNames = [
	"bootstrap",
	"configure",
	"configure.in",
	"Makefile.am",
	"Makefile.in",
	"Makefile",
	"CMakeLists.txt",
	"build.ninja",
	"meson.build",
	# TODO more...?
]

with open("github-token.txt", "r") as fd:
	githubToken = fd.read()

with open("gcc-options.list", "r") as fd:
	compilerFlags = [x.strip() for x in fd.readlines() if not x.isspace()]

with open("repositories.list", "r") as fd:
	repos = [x.strip() for x in fd.readlines() if not x.isspace()]

pool = concurrent.futures.ThreadPoolExecutor(32)
pool.map(checkRepo, repos)
#for repo in repos:
#	checkRepo(repo)
