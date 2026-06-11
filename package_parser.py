import subprocess

apt_result = subprocess.run(
    ['apt', 'list', '--installed'],
    stdout=subprocess.PIPE,
    text=True
    )

for line in apt_result.stdout.splitlines():
    print(line)
