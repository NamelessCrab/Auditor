import subprocess

apt_result = subprocess.run(
    ['apt', 'list', '--installed'],
    stdout=subprocess.PIPE,
    text=True
    )

for line in apt_result.stdout.splitlines()[1:]:
    if '/' in line and 'python3' in line:
        name = line.split('/')[0]
        version = line.split('/')[1]
        version = version.split(' ')[1]
        version = version.split(' ')[0]
        print(name, version)
    
