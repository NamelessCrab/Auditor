import subprocess

result = subprocess.run(['apt', 'list', '--installed'], stdout=PIPE, text=True)

for line in result.stdout.splitlines():
    print(line)