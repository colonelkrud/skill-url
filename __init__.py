from opsdroid.skill import Skill
from opsdroid.matchers import match_regex

import logging

import lxml.html

import aiohttp
import asyncio

class URLSkill(Skill):
    def __init__(self, opsdroid, config):
        super(URLSkill, self).__init__(opsdroid, config)

        self.opsdroid = opsdroid
        self.config = config

    @match_regex(r'(^|\s)(\/)?r\/([a-zA-Z0-9_]*)(?= |$)')
    async def sub_reddit(self, message):
        """Returns the url for a given subredit"""
        text = ("{}, got you fam: ").format(message.user) + ("""<a href="https://www.reddit.com/r/{URL_ID}">r/{URL_ID}</a>""").format(URL_ID=message.regex.group(3))
        await message.respond(text)

    @match_regex(r'(^|\s)(\/)?u\/([a-zA-Z0-9_-]*)(?= |$)')
    async def reddit_user(self, message):
        """Returns the url for a given reddit user"""
        text = ("{}, got you fam: ").format(message.user) + ("""<a href="https://www.reddit.com/user/{URL_ID}">u/{URL_ID}</a>""").format(URL_ID=message.regex.group(3))
        await message.respond(text)

    @match_regex(r'(http(s)?:\/\/)?((w){3}.)?youtu(be|.be|be-nocookie)?(\.com)?\/(watch\?v\=|embed\/|v\/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
    async def youtube_url(self, message):
        """Returns the title for a given youtube url"""
        
        url = 'https://www.youtube.com/watch?v={}'.format(message.regex.group('id'))
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                text = await resp.text()

        # Parse HTML response
        html = lxml.html.fromstring(text)
        video_title = ''.join(html.xpath("//span[@id='eow-title']/@title"))
        await message.respond(video_title)

    @match_regex(r'(?P<everything>(?P<fullURL>(?P<hostname>(?P<protocol>(?:https?:)?\/\/)(?P<subdomain>(?!about\.)[\w-]+?\.)?(?P<domain>[rc]edd(?:it\.com|\.it)))(?!\/(?:blog|about|code|advertising|jobs|rules|wiki|contact|buttons|gold|page|help|prefs|user|message|widget)\b)(?P<subreddit>(?:\/r\/[\w-]+\b(?<!\/pcmasterrace))|(?:\/tb))?(?P<comments>\/comments)??(?P<postID>\/\w{2,7}\b(?<!\/46ijrl)(?<!\/wiki))(?P<everythingElse>(?:(?!\))\S)*)))')
    async def reddit_url(self, message):
        """Returns the title for a given reddit url"""

        url = message.regex.group('everything')
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                text = await resp.text()

        # Parse HTML response
        html = lxml.html.fromstring(text)
        title = ''.join(html.xpath("//title/text()"))
        user = ''.join(html.xpath("(//a[contains(@href,'user')])[1]/text()"))

        response = """<p><b>{title}</b></p>
        <p>Uploaded by: <a href='https://reddit.com/{user}'>{user}</a></p>"""
        await message.respond(response.format(title=title, user=user))
