import re
import requests
import textwrap
import base64
import urllib

from mautrix.types import TextMessageEventContent, MediaMessageEventContent, MessageType, Format, ImageInfo, ContentURI, ThumbnailInfo

from maubot import Plugin, MessageEvent
from maubot.handlers import command

class ToonBot(Plugin):
    async def start(self) -> None:
        await super().start()
        self.toon_urls = {
                'frink': 'https://frinkiac.com',
                'morbo': 'https://morbotron.com',
                'science': 'https://masterofallscience.com'
                }

    async def search_toon(self, toon, query, evt: MessageEvent):
        base_url = self.toon_urls.get(toon)
        api_url = base_url + '/api/search'
        caption_url = base_url + '/api/caption'
        frame = requests.get(api_url + '?q=' + urllib.parse.quote(query)).json()[0]
        episode = frame['Episode']
        timestamp = str(frame['Timestamp'])
        captions_json = requests.get(caption_url + '?e=' + episode + '&t=' + timestamp).json()
        raw_caption_text = "\n".join(list(map(lambda x: x['Content'], captions_json['Subtitles'])))
        captions_wrapped = "\n".join(textwrap.wrap(raw_caption_text, 25))
        captions_encoded = urllib.parse.quote(base64.b64encode(captions_wrapped.encode('utf-8')))
        meme_url = base_url + '/meme/' + episode + '/' + timestamp + '.jpg?b64lines=' + captions_encoded
        meme_binary = requests.get(meme_url).content
        mxc_uri = await self.client.upload_media(meme_binary, mime_type="image/jpeg", filename="image.jpg")
        content = MediaMessageEventContent(
                msgtype=MessageType.IMAGE,
                body=f"image.jpg",
                url=ContentURI(f"{mxc_uri}"),
                info=ImageInfo(
                    mimetype='image/jpeg',
                    width=613,
                    height=460,
                    size=len(meme_binary),
                    thumbnail_url=ContentURI(f"{mxc_uri}"),
                    thumbnail_info=ThumbnailInfo(
                        mimetype="image/jpeg",
                        width=613,
                        height=460,
                        size=len(meme_binary)
                        )
                    )
                )
        await evt.respond(content)

    @command.new()
    @command.argument("message", pass_raw=True, required=True)
    async def frink(self, evt: MessageEvent, message: str = "") -> None:
        await self.search_toon('frink', message, evt)

    @command.new()
    @command.argument("message", pass_raw=True, required=True)
    async def morbo(self, evt: MessageEvent, message: str = "") -> None:
        await self.search_toon('morbo', message, evt)

    @command.new()
    @command.argument("message", pass_raw=True, required=True)
    async def science(self, evt: MessageEvent, message: str = "") -> None:
        await self.search_toon('science', message, evt)
