import sys
from os import chdir,system,listdir
import getopt
import re


# vendor id of AMD
amdgpu_vendor_id = '0x1002'

def set_fan_speed(adapter, percent):
    chdir('/sys/class/drm/card{}/device'.format(adapter))
    vendor_id = '0000'
    with open('vendor') as f:
        vendor_id = f.readline()
        f.close()
    vendor_id = vendor_id.strip('\n')
    # check if the device is AMD GPU by vendor ID
    if vendor_id == amdgpu_vendor_id:
        chdir('/sys/class/drm/card{}/device/hwmon/hwmon{}'.format(adapter, adapter))
        pwm_max = 0
        pwm_min = 0
        pwm = 0
        with open('pwm1_max') as f:
            pwm_max = int(f.readline().strip('\n'))
            f.close()
        
        with open('pwm1_min') as f:
            pwm_min = int(f.readline().strip('\n'))
            f.close()

        pwm_gap = pwm_max - pwm_min
        pwm = int( float(pwm_min) + float(pwm_gap) * float (percent/100.0))
        
        system("echo 1 > pwm1_enable")
        system("echo {} > pwm1".format(pwm))
        # double check pwm
        pwm_set = 0
        with open('pwm1') as f:
            pwm_set = int(f.readline().strip('\n'))
            f.close()
        if pwm_set > pwm - 6 and pwm_set < pwm + 6:
            return True
        else:
            return False

    else:
        return False

if __name__ == '__main__':
    try:
        opts,args = getopt.getopt(sys.argv[1:],"a:s:")
    except getopt.GetoptError:
        print "Usage: amdgpu_fans.py (-a [Adapter No.]) -s [0-100])"
        sys.exit(2)
    adapters = '-1'
    # read command line arguments
    for opt,arg in opts:
        if opt == '-a':
            adapters = str(arg)
            adapters = adapters.split(',')
        if opt == '-s':
            speed = int(arg)

    # if -1 set all GPU speed
    if adapters == '-1':
        adapters = []
        dir_list = listdir('/sys/class/drm')
        for directory in dir_list:
            reg = r'(?<=card)\d*$'
            searchobj = re.search(pattern=reg, string=directory, flags=re.M|re.I)
            if searchobj:
                adapters.append(searchobj.group())

    for adapter in adapters:
        if set_fan_speed(int(adapter), speed):
            print "Set adapter {} to speed {}%".format(adapter, speed)
        else:
            print "Set adapter {} failed, maybe not AMD GPU".format(adapter)

