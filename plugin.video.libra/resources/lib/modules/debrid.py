# -*- coding: utf-8 -*-

'''
    Exodus Add-on
    Copyright (C) 2016 Exodus

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import urllib,json,time,xbmc

from resources.lib.modules import cache
from resources.lib.modules import control
from resources.lib.modules import client


def rdAuthorize():
    try:
        CLIENT_ID = 'X245A4XAIBGVM'
        USER_AGENT = 'Kodi Exodus/3.0'

        if not '' in credentials()['realdebrid'].values():
            if control.yesnoDialog(control.lang(32531).encode('utf-8'), control.lang(32532).encode('utf-8'), '', 'RealDebrid'):
                control.setSetting(id='realdebrid.id', value='')
                control.setSetting(id='realdebrid.secret', value='')
                control.setSetting(id='realdebrid.token', value='')
                control.setSetting(id='realdebrid.refresh', value='')
                control.setSetting(id='realdebrid.auth', value='')
            raise Exception()

        headers = {'User-Agent': USER_AGENT}
        url = 'https://api.real-debrid.com/oauth/v2/device/code?client_id=%s&new_credentials=yes' % (CLIENT_ID)
        result = client.request(url, headers=headers)
        result = json.loads(result)
        verification_url = (control.lang(32533) % result['verification_url']).encode('utf-8')
        user_code = (control.lang(32534) % result['user_code']).encode('utf-8')
        device_code = result['device_code']
        interval = result['interval']

        progressDialog = control.progressDialog
        progressDialog.create('RealDebrid', verification_url, user_code)

        for i in range(0, 3600):
            try:
                if progressDialog.iscanceled(): break
                time.sleep(1)
                if not float(i) % interval == 0: raise Exception()
                url = 'https://api.real-debrid.com/oauth/v2/device/credentials?client_id=%s&code=%s' % (CLIENT_ID, device_code)
                result = client.request(url, headers=headers, error=True)
                result = json.loads(result)
                if 'client_secret' in result: break
            except:
                pass

        try: progressDialog.close()
        except: pass

        id, secret = result['client_id'], result['client_secret']

        url = 'https://api.real-debrid.com/oauth/v2/token'
        post = urllib.urlencode({'client_id': id, 'client_secret': secret, 'code': device_code, 'grant_type': 'http://oauth.net/grant_type/device/1.0'})

        result = client.request(url, post=post, headers=headers)
        result = json.loads(result)

        token, refresh = result['access_token'], result['refresh_token']

        control.setSetting(id='realdebrid.id', value=id)
        control.setSetting(id='realdebrid.secret', value=secret)
        control.setSetting(id='realdebrid.token', value=token)
        control.setSetting(id='realdebrid.refresh', value=refresh)
        control.setSetting(id='realdebrid.auth', value='*************')
        raise Exception()
    except:
        control.openSettings('3.16')


def rdDict():
    try:
        if '' in credentials()['realdebrid'].values(): raise Exception()
        url = 'https://api.real-debrid.com/rest/1.0/hosts/domains'
        result = cache.get(client.request, 24, url)
        hosts = json.loads(result)
        hosts = [i.lower() for i in hosts]
        return hosts
    except:
        return []


def pzDict():
    try:
        if '' in credentials()['premiumize'].values(): raise Exception()
        user, password = credentials()['premiumize']['user'], credentials()['premiumize']['pass']
        url = 'http://api.premiumize.me/pm-api/v1.php?method=hosterlist&params[login]=%s&params[pass]=%s' % (user, password)
        result = cache.get(client.request, 24, url)
        hosts = json.loads(result)['result']['hosterlist']
        hosts = [i.lower() for i in hosts]
        return hosts
    except:
        return []


def adDict():
    try:
        if '' in credentials()['alldebrid'].values(): raise Exception()
        url = 'http://alldebrid.com/api.php?action=get_host'
        result = cache.get(client.request, 24, url)
        hosts = json.loads('[%s]' % result)
        hosts = [i.lower() for i in hosts]
        return hosts
    except:
        return []


def rpDict():
    try:
        if '' in credentials()['rpnet'].values(): raise Exception()
        url = 'http://premium.rpnet.biz/hoster2.json'
        result = cache.get(client.request, 24, url)
        result = json.loads(result)
        hosts = result['supported']
        hosts = [i.lower() for i in hosts]
        return hosts
    except:
        return []


def dlDict():
    try:
        if '' in credentials().get('debridlink', {}).values(): raise Exception()
        url = 'https://debrid-link.fr/api/downloader/status'
        result = cache.get(client.request, 24, url)
        result = json.loads(result)
        host_list = result.get('value', {}).get('hosters', [])
        hosts = [host for status in host_list for host in status.get('hosts', [])]
        return hosts
    except:
        return []


def mdDict():
    try:
        if '' in credentials().get('megadebrid', {}).values(): raise Exception()
        url = 'https://www.mega-debrid.eu/api.php?action=getHostersList'
        result = cache.get(client.request, 24, url)
        result = json.loads(result)
        host_list = result.get('hosters', [])
        hosts = [domain for host in host_list for domain in host.get('domains', [])]
        return hosts
    except:
        return []


def debridDict():
    return {
        'realdebrid': rdDict(),
        'premiumize': pzDict(),
        'alldebrid': adDict(),
        'rpnet': rpDict(),
        'debridlink': dlDict(),
        'megadebrid': mdDict()
    }


def credentials():
    return {
        'realdebrid': {
            'id': control.setting('realdebrid.id'),
            'secret': control.setting('realdebrid.secret'),
            'token': control.setting('realdebrid.token'),
            'refresh': control.setting('realdebrid.refresh')
        },
        'premiumize': {
            'user': control.setting('premiumize.user'),
            'pass': control.setting('premiumize.pin')
        },
        'alldebrid': {
            'user': control.setting('alldebrid.user'),
            'pass': control.setting('alldebrid.pass')
        },
        'rpnet': {
            'user': control.setting('rpnet.user'),
            'pass': control.setting('rpnet.api')
        },
        'debridlink': {
            'user': control.setting('debridlink.user'),
            'pass': control.setting('debridlink.pass')
        },
        'megadebrid': {
            'user': control.setting('megadebrid.user'),
            'pass': control.setting('megadebrid.pass')
        },
        'fshare': {
            'user': control.setting('hktrung@gmail.com'),
            'pass': control.setting('Password')
        }
    }


def status():
    try:
        c = [i for i in credentials().values() if not '' in i.values()]
        if len(c) == 0: return False
        else: return True
    except:
        return False


def resolver(url, debrid):
    u = url
    u = u.replace('filefactory.com/stream/', 'filefactory.com/file/')
    xbmc.log('[plugin.video.libra]::debrid:resolver:' + url, xbmc.LOGNOTICE)

    try:
        if not debrid == 'fshare' and not debrid == True: raise Exception()



    except:
        pass

    try:
        if not debrid == 'megadebrid' and not debrid == True: raise Exception()

        cred = credentials().get('megadebrid', {})

        if '' in cred.values(): raise Exception()
        user, password = cred.get('user'), cred.get('pass')

        result = client.request('https://www.mega-debrid.eu/api.php?action=connectUser&login=%s&password=%s' % (user, password))
        result = json.loads(result)

        if result.get('response_code') == 'ok':
            token = result.get('token')

            post = urllib.urlencode({'link': u})
            result = client.request('https://www.mega-debrid.eu/api.php?action=getLink&token=%s' % token, post=post)
            result = json.loads(result)

            if result.get('response_code') == 'ok':
                return result.get('debridLink', '').strip('"')
    except:
        pass

    return None


