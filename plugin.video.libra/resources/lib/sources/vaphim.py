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

import re, urllib, urlparse, base64, xbmc, string

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import proxy
from resources.lib.modules import control

from resources.lib.modules import servers
from resources.lib.modules import utils


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['vaphim.com']
        self.base_link = 'http://vaphim.com'
        self.moviesearch_link = '/?s=%s'
        self.tvsearch_link = '/?keyword=%s&search_section=2'
        self.username = control.setting('fshare.user')
        self.password = control.setting('fshare.pass')

    def movie(self, imdb, title, localtitle, year):
        try:
            query = self.moviesearch_link % urllib.quote_plus(cleantitle.query(title))
            xbmc.log('[plugin.video.libra]::sources:movie:query:' + query, xbmc.LOGNOTICE)
            query = urlparse.urljoin(self.base_link, query)
            xbmc.log('[plugin.video.libra]::sources:movie:query:' + query, xbmc.LOGNOTICE)

            result = str(proxy.request(query, 'Sẻ chia bất tận'))
            # xbmc.log('[plugin.video.libra]::sources:movie:result:' + result, xbmc.LOGNOTICE)

            if 'page=2' in result or 'page%3D2' in result: result += str(
                proxy.request(query + '&page=2', 'free movies'))

            result = client.parseDOM(result, 'ul', attrs={'class': 'hfeed posts-default clearfix'})
            xbmc.log('[plugin.video.libra]::sources:movie:result::::' + str(result), xbmc.LOGNOTICE)

            result = client.parseDOM(result, 'h3', attrs={'class': 'entry-title'})

            title = cleantitle.get(title)
            years = ['(%s)' % str(year), '(%s)' % str(int(year) + 1), '(%s)' % str(int(year) - 1)]

            xbmc.log('[plugin.video.libra]::sources:movie:title:' + cleantitle.get(title), xbmc.LOGNOTICE)
            xbmc.log('[plugin.video.libra]::sources:movie:year:' + str(years), xbmc.LOGNOTICE)

            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a')) for i in result]
            xbmc.log('[plugin.video.libra]::sources:movie:result:' + str(result), xbmc.LOGNOTICE)

            result = [(i[0][0], i[1][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
            # xbmc.log('[plugin.video.libra]::sources:movie:resultmatch:' + str(result), xbmc.LOGNOTICE)

            result = [i for i in result if any(x in i[1] for x in years)]

            xbmc.log('[plugin.video.libra]::sources:movie:resultyears:' + str(result), xbmc.LOGNOTICE)

            r = [(proxy.parse(i[0]), i[1]) for i in result]
            xbmc.log('[plugin.video.libra]::sources:movie:r:' + str(r), xbmc.LOGNOTICE)

            parsed_title = str(cleantitle.get(i[1])).split('<br/>')
            xbmc.log('[plugin.video.libra]::sources:movie:parsed_title:' + str(parsed_title), xbmc.LOGNOTICE)

            match = [i[0] for i in r if title == parsed_title[1] and '(%s)' % str(year) in i[1]]
            xbmc.log('[plugin.video.libra]::sources:movie:match:' + str(match), xbmc.LOGNOTICE)

            match2 = [i[0] for i in r]
            match2 = [x for y, x in enumerate(match2) if x not in match2[:y]]
            xbmc.log('[plugin.video.libra]::sources:movie:match2:' + str(match2), xbmc.LOGNOTICE)
            if match2 == []: return

            for i in match2[:5]:
                try:
                    if len(match) > 0: url = match[0]; break
                    r = proxy.request(urlparse.urljoin(self.base_link, i), 'Sẻ chia bất tận')
                    r = re.findall('(tt\d+)', r)
                    if imdb in r: url = i; break
                except:
                    pass

            url = re.findall('(?://.+?|)(/.+)', url)[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            xbmc.log('[plugin.video.libra]::movie:url:' + url, xbmc.LOGNOTICE)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, year):
        try:
            query = self.tvsearch_link % urllib.quote_plus(cleantitle.query(tvshowtitle))
            query = urlparse.urljoin(self.base_link, query)

            result = str(proxy.request(query, 'free movies'))
            if 'page=2' in result or 'page%3D2' in result: result += str(
                proxy.request(query + '&page=2', 'free movies'))

            result = client.parseDOM(result, 'div', attrs={'class': 'item'})

            tvshowtitle = 'watch' + cleantitle.get(tvshowtitle)
            years = ['(%s)' % str(year), '(%s)' % str(int(year) + 1), '(%s)' % str(int(year) - 1)]

            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title')) for i in result]
            result = [(i[0][0], i[1][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
            result = [i for i in result if any(x in i[1] for x in years)]

            r = [(proxy.parse(i[0]), i[1]) for i in result]

            match = [i[0] for i in r if tvshowtitle == cleantitle.get(i[1]) and '(%s)' % str(year) in i[1]]

            match2 = [i[0] for i in r]
            match2 = [x for y, x in enumerate(match2) if x not in match2[:y]]
            if match2 == []: return

            for i in match2[:5]:
                try:
                    if len(match) > 0: url = match[0]; break
                    r = proxy.request(urlparse.urljoin(self.base_link, i), 'free movies')
                    r = re.findall('(tt\d+)', r)
                    if imdb in r: url = i; break
                except:
                    pass

            url = re.findall('(?://.+?|)(/.+)', url)[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = urlparse.urljoin(self.base_link, url)

            result = proxy.request(url, 'tv_episode_item')
            result = client.parseDOM(result, 'div', attrs={'class': 'tv_episode_item'})

            title = cleantitle.get(title)
            premiered = re.compile('(\d{4})-(\d{2})-(\d{2})').findall(premiered)[0]
            premiered = '%s %01d %s' % (
            premiered[1].replace('01', 'January').replace('02', 'February').replace('03', 'March').replace('04',
                                                                                                           'April').replace(
                '05', 'May').replace('06', 'June').replace('07', 'July').replace('08', 'August').replace('09',
                                                                                                         'September').replace(
                '10', 'October').replace('11', 'November').replace('12', 'December'), int(premiered[2]), premiered[0])

            result = [(client.parseDOM(i, 'a', ret='href'),
                       client.parseDOM(i, 'span', attrs={'class': 'tv_episode_name'}),
                       client.parseDOM(i, 'span', attrs={'class': 'tv_num_versions'})) for i in result]
            result = [(i[0], i[1][0], i[2]) for i in result if len(i[1]) > 0] + [(i[0], None, i[2]) for i in result if
                                                                                 len(i[1]) == 0]
            result = [(i[0], i[1], i[2][0]) for i in result if len(i[2]) > 0] + [(i[0], i[1], None) for i in result if
                                                                                 len(i[2]) == 0]
            result = [(i[0][0], i[1], i[2]) for i in result if len(i[0]) > 0]

            url = [i for i in result if title == cleantitle.get(i[1]) and premiered == i[2]][:1]
            if len(url) == 0: url = [i for i in result if premiered == i[2]]
            if len(url) == 0 or len(url) > 1: url = [i for i in result if
                                                     'season-%01d-episode-%01d' % (int(season), int(episode)) in i[0]]

            url = url[0][0]
            url = proxy.parse(url)
            url = re.findall('(?://.+?|)(/.+)', url)[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)
            xbmc.log('[plugin.video.libra]::sources:url:' + url, xbmc.LOGNOTICE)

            result = proxy.request(url, 'wordpress-post-tabs')
            # xbmc.log('[plugin.video.libra]::sources:result:' + str(result), xbmc.LOGNOTICE)

            links = client.parseDOM(result, 'div', attrs={'id': 'tabs.+?'})
            xbmc.log('[plugin.video.libra]::sources:links:' + str(links), xbmc.LOGNOTICE)

            for i in links:
                try:
                    gotLink = [client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a')]
                    xbmc.log('[plugin.video.libra]::sources:gotLink:' + str(gotLink[1]), xbmc.LOGNOTICE)

                    url = gotLink[0]
                    url = [x for x in url if 'www.fshare.vn' in x][-1]
                    url = url.encode('utf-8')

                    xbmc.log('[plugin.video.libra]::sources:url:' + str(url), xbmc.LOGNOTICE)

                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                    host = host.encode('utf-8')
                    xbmc.log('[plugin.video.libra]::sources:host:' + str(host), xbmc.LOGNOTICE)

                    quality = 'HD'
                    xbmc.log('[plugin.video.libra]::sources:quality:' + str(quality), xbmc.LOGNOTICE)

                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False,
                                    'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        xbmc.log('[plugin.video.libra]::vaphim:resolve:url:' + str(url), xbmc.LOGNOTICE)
        fs = servers.fshare(self.username, self.password)
        sleep = 2000
        for loop in range(3):
            if loop > 0:
                xbmc.log('[plugin.video.libra]::resolve:direct_link:' + str(direct_link), xbmc.LOGNOTICE)

            direct_link = fs.get_maxlink(url)
            if direct_link and direct_link not in 'fail-noFile':
                break
            elif direct_link == 'noFile':
                direct_link = 'fail'
                break
            else:
                xbmc.sleep(sleep)
                sleep += 1000

        fs.logout()
        xbmc.log('[plugin.video.libra]::resolve:direct_link:' + str(direct_link), xbmc.LOGNOTICE)
        return direct_link
