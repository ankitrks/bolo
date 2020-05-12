import os
import requests

def run():
    file_str = ''
    # check when was the list updated last: https://www.dan.me.uk/tornodes
    r = requests.get('https://www.dan.me.uk/torlist/')

    if r.status_code == 200:
        for a in r.content.split('\n'):
            if a:
                file_str += 'deny ' + str(a) + ';\n'

        file_str += 'deny 109.70.100.25;\ndeny 109.70.100.24;\ndeny 109.70.100.35;\ndeny 109.70.100.32;\ndeny 109.70.100.33;\ndeny 109.70.100.29;\ndeny 109.70.100.20;\n'
        f = open('/etc/nginx/tor-ip.conf', 'w')
        f.write(file_str)
        f.close()
        os.system('sudo service nginx reload')

