import os
import re
import requests

node_name = os.getenv("NODE_NAME")
enable = True
node_score = 0

mem_info = os.popen('cat /proc/meminfo | grep MemAvailable').read()
mem_free = float(re.split(r'\s+', mem_info)[1])/1000000
if mem_free > 100:
  mem_free = 100
if mem_free < 3:
  enable = False

cpu_num = int(os.popen('grep \'model name\' /proc/cpuinfo | wc -l').read())
cpu_info = os.popen('cat /proc/loadavg').read()
cpu_load = float(re.split(r'\s+', cpu_info)[0])
if cpu_load > 2 * cpu_num:
  enable = False
cpu_free = 2 * cpu_num - cpu_load

if enable:
  node_score = int((mem_free + cpu_free)/10)

print('score of ' + node_name + ':' + str(node_score))

jenkins_url = 'http://192.168.0.201:8080'
username = 'jenkins'

script = '''
import jenkins.*
import jenkins.model.*
import hudson.*
import hudson.model.*
import jp.ikedam.jenkins.plugins.scoringloadbalancer.preferences.*

for (aSlave in hudson.model.Hudson.instance.slaves) {
    if (aSlave.name == \'''' + node_name + '''\') {
        aSlave.getNodeProperty('jp.ikedam.jenkins.plugins.scoringloadbalancer.preferences.BuildPreferenceNodeProperty').preference=''' + str(node_score) + '''
    }
}
'''

#print(script)

import jenkins

server = jenkins.Jenkins(jenkins_url, username, username)
info = server.run_script(script)
print(info)
