# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Before App Launch Hook

This hook is executed prior to application launch and is useful if you need
to set environment variables or run scripts as part of the app initialization.
"""

import os
import sys
import logging
import tank


class BeforeAppLaunch(tank.Hook):
    """
    Hook to set up the system prior to app launch.
    """

    def execute(self, app_path, app_args, version, **kwargs):
        """
        The execute function of the hook will be called prior to starting
        the required application

        :param app_path: (str) The path of the application executable
        :param app_args: (str) Any arguments the application may require
        :param version: (str) version of the application being run if set in
                        the "versions" settings of the Launcher instance,
                        otherwise None

        """

        # accessing the current context (current shot, etc)
        # can be done via the parent object
        multi_launchapp = self.parent
        current_entity = multi_launchapp.context.entity

        logging.info("Setting Global Variable for THR3d")

        # Engine specific functions
        multi_launchapp = self.parent
        if multi_launchapp.get_setting("engine") == "tk-houdini":
            logging.info("Running Houdini")
            logging.info("Running Houdini")
            os.environ["HOUDINI_USE_OTL_AS_DEFAULT_HDA_EXT"] = 1
            os.environ["HOUDINI_OTLSCAN_PATH"] = r"\\isln-smb\thr3dcgi_config\Houdini\otl"

        if multi_launchapp.get_setting("engine") == "tk-maya":
            logging.info("Running Maya", version)
            logging.info("app_path == > ", app_path)
            logging.info("app_args == > ", app_args)
            logging.info("kwargs == > ", kwargs)
            logging.info("current_entity == > ", current_entity)
