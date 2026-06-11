import subprocess

apt_result = subprocess.run(
    ['apt', 'list', '--installed'],
    stdout=PIPE,
    text=True
    )

apt_lines = apt_result.stdout.splitlines()
print(apt_lines)
'''
for line in result.stdout.splitlines():
    print(line)
'''