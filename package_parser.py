import subprocess

apt_result = subprocess.run(
    ['apt', 'list', '--installed'],
    stdout=subprocess.PIPE,
    text=True
    )
package_dict = {
    'name': [],
    'version': []
}
for line in apt_result.stdout.splitlines()[1:]:
    if '/' in line:
        package_dict['name'].append(line.split('/')[0])
        version = line.split('/')[1]
        version = version.split(' ')[1]
        version = version.split(' ')[0]
        package_dict['version'].append(version)

print(package_dict)
    
        

