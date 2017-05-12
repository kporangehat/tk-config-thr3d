# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.
import sgtk
import os
import sys

HookBaseClass = sgtk.get_hook_baseclass()

class ScreeningroomInit(HookBaseClass):
    """
    Controls the initialization in and around screening room
    """
        
    def before_rv_launch(self, path):
        """
        Executed before RV is being launched        
        
        :param path: The path to the RV that is about to be launched
        :type path: str
        """

        # accessing the current context (current shot, etc)
        # can be done via the parent object
        #
        # > app = self.parent
        # > current_entity = app.context.entity
        
        # you can set environment variables like this:
        # os.environ["MY_SETTING"] = "foo bar"
        desktop_qt_path = r"C:\Program Files\Shotgun\Qt\bin"
        if desktop_qt_path in os.environ.get("PATH"):
            try:
                sys.path.remove(desktop_qt_path)
                self.parent.logger.warning("Removed Desktop QT: %s" % desktop_qt_path)
            except ValueError:
                self.parent.logger.warning("%s not in PATH" % desktop_qt_path)
                self.parent.logger.warning("PATH: %s" % os.environ.get("PATH"))


