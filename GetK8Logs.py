#############################################################################################
#
#  This script is intended to make it very simple to dump out all logs from a K8 cluster
#  to a local file system for use in troubleshooting and in preparation for supplying them
#  to a support organisatoin
#
#  It assumes there is a preconfigured kubectl and:
#  - Creates a logs subfolder
#  - Gets a list of all pods
#  - Gets a description of each pod and writes it to file
#  - Gets the logs for the current containers of each pod and writes them to a file
#  - Gets the logs for previous instances of each pod (where they exist) and write them to file
#
#  This has been tested on a very small number of Windows and Linux environments
#  Use at your own risk
#
############################################################################################

import os
import subprocess
import platform

Windows = False
if (platform.system() == 'Windows'):
        Windows = True
if(Windows):
        #If we are on Windows, we want to make sure the processes open in the background
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

result = ''

#Check if the logs folder exists, if not create it
try:
        os.makedirs('logs')
except FileExistsError:
        pass

#Get a list of all pods
print('Retrieving list of all pods')
if(Windows):
        result = subprocess.run(['kubectl', 'get','pods','--no-headers'], stdout=subprocess.PIPE, startupinfo=si)
else:
        result = subprocess.run(['kubectl', 'get','pods','--no-headers'], stdout=subprocess.PIPE)
result = result.stdout.decode('utf-8').split('\n')
total = len(result) - 1
podCounter = 0

for line in result:
        x = line.split(' ', maxsplit=2)[0]
        if(x!= ''):
                logs = ''
                describe = ''
                podCounter += 1
                podCount = '(' + str(podCounter) + '/' + str(total) + ')'
                
                print('Retrieving pod description for', x, podCount)
                if(Windows):
                        describe = subprocess.run(['kubectl', 'describe', 'pod', x], stdout=subprocess.PIPE, startupinfo=si)
                else:
                        describe = subprocess.run(['kubectl', 'describe', 'pod', x], stdout=subprocess.PIPE)
                describe = describe.stdout.decode('utf-8')
                print('Writing pod description for', x, 'to logs' + os.sep + x + '.describe')
                f = open('logs' + os.sep + x + '.describe', 'w')
                f.write(describe)
                f.close()

                print('Retrieving logs for', x, podCount)
                if(Windows):
                        logs = subprocess.run(['kubectl', 'logs', x, '--all-containers'], stdout=subprocess.PIPE, startupinfo=si)
                else:
                        logs = subprocess.run(['kubectl', 'logs', x, '--all-containers'], stdout=subprocess.PIPE)
                logs = logs.stdout.decode('utf-8')
                print('Writing logs for', x, 'to logs' + os.sep + x + '.log')
                f = open('logs' + os.sep + x + '.log', 'w')
                f.write(logs)
                f.close()

                print('Checking for logs from previous instances of', x, podCount)
                if(Windows):
                        logs = subprocess.run(['kubectl', 'logs', '-p', x, '--all-containers'], stdout=subprocess.PIPE, startupinfo=si)
                else:
                        logs = subprocess.run(['kubectl', 'logs', '-p', x, '--all-containers'], stdout=subprocess.PIPE)
                logs = logs.stdout.decode('utf-8')
                if(logs != ''): #Filter out instances with no previous logs
                        print('Writing logs for', x, 'to logs' + os.sep + x + '_old.log')
                        f = open('logs' + os.sep + x + '_old.log', 'w')
                        f.write(logs)
                        f.close()
                 

                
