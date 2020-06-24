import re
from django.shortcuts import render
from libvirt import libvirtError
from instances.models import Instance
from vrtManager.instance import wvmInstance
from webvirtcloud.settings import WS_PUBLIC_PORT, WS_PUBLIC_HOST


def console(request):
    """
    :param request:
    :return:
    """
    console_error = None

    if request.method == 'GET':
        token = request.GET.get('token', '')
        view_type = request.GET.get('view', 'lite')
        view_only = request.GET.get('view_only', 0)
        scale = request.GET.get('scale', 0)
        resize_session = request.GET.get('resize_session', 0)
        clip_viewport = request.GET.get('clip_viewport', 0)

    try:
        temptoken = token.split('-', 1)
        host = int(temptoken[0])
        uuid = temptoken[1]
        instance = Instance.objects.get(compute_id=host, uuid=uuid)
        conn = wvmInstance(instance.compute.hostname,
                           instance.compute.login,
                           instance.compute.password,
                           instance.compute.type,
                           instance.name)
        console_type = conn.get_console_type()
        console_websocket_port = conn.get_console_websocket_port()
        console_passwd = conn.get_console_passwd()
    except libvirtError:
        console_type = None
        console_websocket_port = None
        console_passwd = None

    ws_port = console_websocket_port if console_websocket_port else WS_PUBLIC_PORT
    ws_host = WS_PUBLIC_HOST if WS_PUBLIC_HOST else request.get_host()

    if ':' in ws_host:
        ws_host = re.sub(':[0-9]+', '', ws_host)

    console_page = "console-" + console_type + "-" + view_type + ".html"
    if console_type == 'vnc' or console_type == 'spice':
        response = render(request, console_page, locals())
    else:
        console_error = f"Console type: {console_type} no support"
        response = render(request, 'console-vnc-lite.html', locals())

    response.set_cookie('token', token)
    return response
