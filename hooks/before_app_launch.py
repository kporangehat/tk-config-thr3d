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

# TODO: IT needs to add this
THR3D_CGI_CONFIG = os.environ.get('THR3D_CGI_CONFIG',
                                  r'\\isln-smb\thr3dcgi_config')

if not os.path.exists(THR3D_CGI_CONFIG):
    logging.error("Can't access to config path: {}".format(THR3D_CGI_CONFIG))
    raise ValueError

if THR3D_CGI_CONFIG not in sys.path:
    sys.path.append(THR3D_CGI_CONFIG)

try:
    import Agnostic
except ImportError:
    logging.error("THR3D was not able to load the Agnostic")
    raise ImportError

from shotgun_utils import time_log_utils, main_utils


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

        logging.info("Setting Up for THR3D Pipeline")

        # accessing the current context (current shot, etc)
        # can be done via the parent object
        multi_launchapp = self.parent

        project_entity = multi_launchapp.context.project
        user_entity = multi_launchapp.context.user
        task_entity = multi_launchapp.context.task

        if task_entity:
            # Start time logging
            time_log_utils.start_timelog_clock(project=project_entity,
                                               task=task_entity,
                                               user=user_entity)

            # Change the task's status
            result = main_utils.set_status(task_entity, 'ip')
            if result:
                logging.info("Updated the status of entity: {} - id: {} to "
                             "{}".format(result.get('name'),
                                         result.get('id'),
                                         result.get('sg_status_list')))
            else:
                logging.info("Failed to update the status.")

        # Engine specific functions
        if multi_launchapp.get_setting("engine") == "tk-nuke":
            logging.info("Running Before Launch Functions for Nuke")
            # TODO, we need to remove this from here once the Nuke stuff is
            # finished
            os.environ['NUKE_PATH'] += r";\\isln-smb\aw_config\Git_Live_Code\Software\Nuke"

        if multi_launchapp.get_setting("engine") == "tk-houdini":
            logging.info("Running Before Launch Functions for Houdini")
            os.environ["HOUDINI_USE_OTL_AS_DEFAULT_HDA_EXT"] = "1"
            houdini_otl = os.path.join(Agnostic.THR3D_HOUDINI, "otl")
            if "HOUDINI_OTLSCAN_PATH" in os.environ:
                os.environ["HOUDINI_OTLSCAN_PATH"] += ";" + houdini_otl
            else:
                os.environ["HOUDINI_OTLSCAN_PATH"] = houdini_otl

        if multi_launchapp.get_setting("engine") == "tk-maya":
            logging.info("Running Before Launch Functions for Maya")
            mel_script_path = os.path.join(Agnostic.THR3D_MAYA, "mel")
            if "MAYA_SCRIPT_PATH" in os.environ:
                os.environ["MAYA_SCRIPT_PATH"] += ";"+mel_script_path
            else:
                os.environ["MAYA_SCRIPT_PATH"] = mel_script_path
