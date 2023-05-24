import sys
import subprocess
from ualfred import Workflow3


def main(wf):
    clashx_format = 'export https_proxy=http://{ip}:{port} http_proxy=http://{ip}:{port} all_proxy=socks5://{ip}:{port}'
    command = "ifconfig -a | grep '^[^[:space:]]' | awk '{print $1}' | while read iface; do addr=$(ifconfig ${" \
              "iface%:} | grep 'inet ' | awk '{print $2}'); if [ ! -z \"$addr\" ]; then echo \"${iface%:} $addr\"; " \
              "fi; done"

    select_iface = ''
    clashx_port = '7890'

    argv = []
    if len(wf.args):
        argv = str(wf.args[0]).split()
    if len(argv) > 0:
        select_iface = argv[0] or ''
    if len(argv) > 1:
        clashx_port = argv[1] or '7890'

    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        error = result.stderr.decode('utf-8')
        wf.add_item(title="Error: " + error, valid=False)
        wf.send_feedback()
        return

    output = result.stdout.decode('utf-8')

    id = 0
    for line in output.split('\n'):
        if not line:
            continue
        iface, ip = line.split()
        if iface.startswith(select_iface) or select_iface == '':
            proxy_cmd = clashx_format.format(ip=ip, port=clashx_port)
            wf.add_item(title=iface, arg=proxy_cmd, subtitle=proxy_cmd, uid=id, valid=True)
            id += 1
    wf.send_feedback()


if __name__ == "__main__":
    wf = Workflow3()
    sys.exit(wf.run(main))
