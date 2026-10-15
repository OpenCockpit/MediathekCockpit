# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


from Components.config import config
from Screens.ChoiceBox import ChoiceBox
from .Debug import logger
from .__init__ import _
from .CockpitPlayer import CockpitPlayer


class MediathekPlayer(CockpitPlayer):
    """CockpitPlayer that, if "Stop movie behaviour" is set to "Ask user", asks what to do when the movie is stopped
    or has ended: quit, restart from the beginning, or continue."""

    def askToLeave(self):
        return config.plugins.mediathekcockpit.askstopmovie.value == "ask"

    def leavePlayer(self):
        logger.info("...")
        if self.askToLeave():
            self.openLeaveChoice()
        else:
            CockpitPlayer.leavePlayer(self)

    def doEofInternal(self, playing):
        logger.info("playing: %s, self.execing: %s", playing, self.execing)
        if self.askToLeave():
            if self.execing:
                self.openLeaveChoice()
        else:
            CockpitPlayer.doEofInternal(self, playing)

    def openLeaveChoice(self):
        choices = [
            (_("Quit"), "quit"),
            (_("Restart from the beginning"), "restart"),
            (_("Continue playing"), "continue"),
        ]
        self.session.openWithCallback(self.leaveChoiceCallback, ChoiceBox, title=_("Action"), list=choices)

    def leaveChoiceCallback(self, answer):
        answer = answer and answer[1]
        logger.info("answer: %s", answer)
        if answer == "quit":
            CockpitPlayer.leavePlayer(self)
        elif answer == "restart":
            self.doSeek(0)
            self.setSeekState(self.SEEK_STATE_PLAY)
        # "continue", or the box was cancelled: carry on
