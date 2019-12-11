from jarvis.models import FCMDevice

from datetime import datetime
import json

def run():
    devices = FCMDevice.objects.filter(user__st__is_test_user=False, is_uninstalled=False)
    for device in devices:
        t = device.send_message(data={'uninstall_tracking': 'true'})
        try:
            if t[1]['results'][0]['error'] == 'NotRegistered':
                print 'not installed', t
                device.is_uninstalled=True
                device.uninstalled_date=datetime.now()
                list_data=[]
                if device.uninstalled_desc:
                    list_data = json.loads(device.uninstalled_desc)
                list_data.append({'uninstall': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                device.uninstalled_desc=json.dumps(list_data)
                device.save()
        except Exception as e:
            print e
            print 'installed', t
            pass
