from django.shortcuts import render, HttpResponse
from django.core.cache import cache
cache.clear()
import sys
import os
import urllib
import urllib2
import json
import zipfile
import requests

api_url = 'https://api.github.com/repos/'
commits = '/commits'
list_holder = []
file_amount = []
O_auth = '' #enter your client_id & secret URL to avoid the rate limit(max 60/h)

#get the top ten commits of a repository
def get_top():
	for commit in list_holder:
		fileData = getFiles(commit['repo'], commit['sha'])
		count = listFiles(fileData)
		sortedList = sorted(count, key=lambda k : k['amount'])
		sortedList = sortedList[:10]
		for key, value in enumerate(sortedList):
			value['position'] = key + 1
	return (sortedList)
	
#Get the necessary commit info
def get_commit_info(repo_name):
	data = {}
	formattedData = []
	url = api_url + repo_name + commits + O_auth
	req = urllib2.urlopen(url)
	data = json.load(req)
	for commit in data:
		commit_holder = {}
		repo = repo_name
		sha_id = commit['sha']
		message = commit['commit']['message']
		committer = commit['commit']['committer']
		commit_holder['repo'] = repo
		commit_holder['sha'] = sha_id
		commit_holder['name'] = committer['name']
		commit_holder['date'] = committer['date'][:10]
		commit_holder['email'] = committer['email']
		commit_holder['message'] = message
		list_holder.append(commit_holder)

#get the files in the repository
def getFiles(repo_name, sha_id):
    fileHolder = {}
    url = api_url + repo_name + commits + '/' + sha_id + O_auth
    req = urllib2.urlopen(url)
    fileHolder = json.load(req)
    files = fileHolder['files']
    returnedFileData = []
    for file in files:
        fileData = {}
        fileData['repo'] = repo_name
        fileData['filename'] = file['filename']
        fileData['status'] = file['status']
        returnedFileData.append(fileData)
    return returnedFileData


#get the amount of times a file has been commited
def listFiles(fileData):
	for file in fileData:
		print (file)
		file_holder = {}      
		if len(file_amount) > 0:
			for x, amount in enumerate(file_amount):           
				if file['filename'] == file_amount[x]['filename']:
					result = filter(lambda l: l['filename'] == 
					file['filename'] and l['repo'] == file['repo'], file_amount)
					if result != None:
						file_amount[x]['amount'] +=1
						break
					else:
						file_holder['repo'] = file['repo']
						file_holder['filename'] = file['filename']
						file_holder['amount'] = 1
						file_amount.append(file_holder)
						break
				else:
					file_holder['repo'] = file['repo']
					file_holder['filename'] = file['filename']
					file_holder['amount'] = 1
					file_amount.append(file_holder)
					break
		else:
			file_holder['repo'] = file['repo']
			file_holder['filename'] = file['filename']
			file_holder['amount'] = 1
			file_amount.append(file_holder)
	return file_amount
	
#download zip in map GRD on desktop
def dl_file(owner, repo, size):
	if size > 0:
		try:
			type_file = 'ZIP'
			userhome = os.path.expanduser('~')
			directory = userhome + '/Desktop/GRD/'
			name_file = owner + '_' + repo +'.'+type_file
			name_file = repo +'.'+type_file
			if not os.path.exists(directory):
				os.makedirs(directory)
			url = api_url + owner + '/' + repo + '/zipball/master' + O_auth
			save_location = directory + name_file
			urllib.urlretrieve (url, save_location)
			unzip(name_file, owner, size)
		except:
			print('bad zip file')
		
		
#unzip file in map GRD on desktop
def unzip(zipName, size):
	if size > 0:
		userhome = os.path.expanduser('~')
		directory = userhome + '/Desktop/GRD/'
		path = directory + zipName
		with zipfile.ZipFile(path, 'r') as z:
			z.extractall(directory)

#check if the url ends in '/' 
def checkUrl(url):
	if url[-1] == '/':
		url = url[:-1]
	return url

#get size of repository
def getSize(url):
	req = requests.get(url)
	repoData = {}
	jsonList = []
	jsonList.append(req.json())
	repoData[0] = jsonList[0]
	for key, value in repoData[0].items():
		if key == 'size':
			size = value
	return size

#list page
def list(request):
	output = {}
	if request.method == 'POST':
		list_urls_commits = []
		list_commits = []
		list_urls = []
		get_list = request.POST.get('list_urls')
		list_urls = str(get_list).split(';')
		for repo_url in list_urls:
			repo_url = checkUrl(repo_url)
			repo_name = repo_url.split('/')[-1]
			owner = repo_url.split('/')[-2]
			repo = owner + '/' + repo_name
			size_holder = (api_url + owner + '/' + repo_name + O_auth)
			size = getSize(size_holder)
			if (size > 0):
				get_commit_info(repo)
				dl_file(owner, repo_name, size)
		if (size > 0):
			most_changed = get_top()
			output['topten'] = most_changed
			output['info'] = list_holder
		return render(request, 'grd/commits.html', {'output': output})
	return render(request, 'grd/list.html')
	
#index page
def index(request):
	output = {}
	if request.method == 'POST':
		list_urls = [value for name, value in request.POST.items()
					if name.startswith('repo_url')]
		for repo_url in list_urls:
			repo_url = checkUrl(repo_url)
			repo_name = repo_url.split('/')[-1]
			owner = repo_url.split('/')[-2]
			repo = owner + '/' + repo_name
			size_holder = (api_url +owner+'/'+repo_name + O_auth)
			size = getSize(size_holder)
			if (size > 0):
				get_commit_info(repo)
				dl_file(owner, repo_name, size)
		if (size > 0):
			most_changed = get_top()
			output['topten'] = most_changed
			output['info'] = list_holder
		return render(request, 'grd/commits.html', {'output': output})
	return render(request, 'grd/index.html')