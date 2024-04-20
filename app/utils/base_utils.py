import sys
import requests

from termcolor import cprint


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WHITE = '\033[97m'


def is_hex(s):
    try:
        int(s, 16)
        return True
    except:
        return False


def _hex_to_int(s):
    hex_int = round(int(s, 16)/10**18, 8)
    if hex_int == 0:
        return int(s, 16)
    return hex_int


def kvPrint(key, value, key_color="OKGREEN", value_color="WARNING"):
    key_width = 18
    key_value = 3
    failure_list = ['False', "Failure"]
    if any(s.lower() in str(value).lower() for s in failure_list):
        value_color = "FAIL"

    key_color_attr = getattr(bcolors, key_color)
    value_color_attr = getattr(bcolors, value_color)
    print(key_color_attr + "◆ {:<{key_width}} : ".format(key, key_width=key_width) + bcolors.ENDC, end="")
    print(value_color_attr + "{:>{key_value}} ".format(str(value), key_value=key_value) + bcolors.ENDC)


def dump(obj, nested_level=0, output=sys.stdout, hex_to_int=False):
    spacing = '   '
    def_spacing = '   '
    if type(obj) == dict:
        print('%s{' % (def_spacing + (nested_level) * spacing))
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print(bcolors.OKGREEN + '%s%s:' % (def_spacing + (nested_level + 1) * spacing, k) + bcolors.ENDC, end="")
                dump(v, nested_level + 1, output, hex_to_int)
            else:
                # print >>  bcolors.OKGREEN + '%s%s: %s' % ( (nested_level + 1) * spacing, k, v) + bcolors.ENDC
                print(bcolors.OKGREEN + '%s%s:' % (def_spacing + (nested_level + 1) * spacing, k) + bcolors.WARNING + ' %s' % v + bcolors.ENDC,
                      file=output)
        print('%s}' % (def_spacing + nested_level * spacing), file=output)
    elif type(obj) == list:
        print('%s[' % (def_spacing + (nested_level) * spacing), file=output)
        for v in obj:
            if hasattr(v, '__iter__'):
                dump(v, nested_level + 1, output, hex_to_int)
            else:
                print(bcolors.WARNING + '%s%s' % (def_spacing + (nested_level + 1) * spacing, v) + bcolors.ENDC, file=output)
        print('%s]' % (def_spacing + (nested_level) * spacing), file=output)
    else:
        if hex_to_int and is_hex(obj):
            print(bcolors.WARNING + '%s%s' % (def_spacing + nested_level * spacing, str(_hex_to_int(obj)) + bcolors.ENDC))
        else:
            print(bcolors.WARNING + '%s%s' % (def_spacing + nested_level * spacing, obj) + bcolors.ENDC)


def append_http(url):
    if "http://" not in url and "https://" not in url:
        url = f"http://{url}"
    return url


def jequest(url, method="get", payload={}, elapsed=False, print_error=False, headers={}, files=None, debug=False):
    (json, data, http_version, r_headers, error) = ({}, {}, None, None, None)
    url = append_http(url)
    TIMEOUT = 10
    if debug:
        cprint(f"url='{url}', method='{method}', payload='{payload}', files={files}, headers={headers}")

    if method not in ("get", "post", "patch", "delete"):
        cprint(f"unsupported method={method}, url={url} ", "error")
        return {"error": "unsupported method"}
    try:
        func = getattr(requests, method)
        if method == "get":
            response = func(url, verify=False, timeout=TIMEOUT, headers=headers)
        else:
            response = func(url, json=payload, verify=False, timeout=TIMEOUT, headers=headers, files=files)
        http_version = response.raw.version
        r_headers = response.headers

    except requests.exceptions.HTTPError as errh:
        error = errh
        if debug:
            kvPrint("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        error = errc
        if debug:
            kvPrint("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        error = errt
        if debug:
            kvPrint("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        error = err
        if debug:
            kvPrint("OOps: Something Else", err)

    # cprint(f"{url}, {method}, {payload} , {response.status_code}", "green")
    try:
        response_code = response.status_code
    except:
        response_code = 999

    if response_code != 999:
        try:
            json = response.json()
        except:
            json = {}
            data['text'] = response.text

        if elapsed:
            data['elapsed'] = int(response.elapsed.total_seconds() * 1000)
            if len(json) > 0:
                json['elapsed'] = data['elapsed']

    if response_code > 200 and response_code != 999:
        # cprint(f"status_code: {response_code} , url: {url} , payload: {payload}, response: {data.get('text')}", "red")
        if json.get("error"):
            error = json['error']['message']
        if print_error:
            cprint(f"status_code: {response_code}, url: {url}, error: {error}, payload: {payload},response: {response.text}", "red")

    data['status_code'] = response_code
    data['http_version'] = http_version
    data['r_headers'] = r_headers
    data['result'] = json
    data['error'] = error

    if debug:
        dump(data)
    return data