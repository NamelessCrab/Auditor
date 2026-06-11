import subprocess

apt_result = subprocess.run(
    ['apt', 'list', '--installed'],
    stdout=subprocess.PIPE,
    text=True
    )

apt_lines = apt_result.stdout.splitlines()
p_ids = []
for line in apt_lines:
    id = line.index('python3')
    p_ids.append[apt_lines[id]]
        
print(p_ids)

'''
for line in result.stdout.splitlines():
    print(line)
'''