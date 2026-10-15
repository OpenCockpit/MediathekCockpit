# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


import json
from Screens.ChoiceBox import ChoiceBox
from .WebRequests import WebRequests
from .FileUtils import readFile
from .Constants import plugindir
from .Debug import logger
from .__init__ import _


class ChannelSelection():
    def __init__(self):
        return

    def getChannelList(self):
        """The broadcasters from the service; the list delivered with the plugin if the service doesn't answer."""
        url = "https://mediathekviewweb.de/api/channels"
        channel_list = []
        try:
            channel_list = json.loads(WebRequests().getContent(url)).get("channels", [])
        except Exception as e:
            logger.error("channel list request failed: %s", e)
        if not channel_list:
            logger.info("using the channel list of the plugin")
            try:
                channel_list = json.loads(readFile(plugindir + "channels/mtc_channels.json")).get("channels", [])
            except Exception as e:
                logger.error("channel list of the plugin unreadable: %s", e)
        return channel_list

    def openChannelSelection(self):
        logger.info("...")
        channel_list = self.getChannelList()
        choices = [(_("All channels"),)]
        for channel in channel_list:
            choices.append((str(channel),))
        self.session.openWithCallback(
            self.openChannelSelectionCallback,
            ChoiceBox,
            title=_("Channel selection"),
            list=choices,
            titlebartext="MediathekCockpit" + " - " + _("Channel selection"),
            keys=[]
        )

    def openChannelSelectionCallback(self, selection):
        logger.info("selection: %s", selection)
        if selection:
            channel = selection[0]
            if channel == _("All channels"):
                if "queries" in self.postdata:
                    del self.postdata["queries"]
                channel = None
            else:
                self.postdata["queries"] = [
                    {"fields": ["channel"], "query": channel}]
            self.postdata["offset"] = 0
            self.downloadMovieList(channel)
