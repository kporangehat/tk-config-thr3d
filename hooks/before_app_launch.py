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


# TODO: Add this to path via systems(This is too hard coded)
sys.path.append(r"\\isln-smb\thr3dcgi_config\Apps\Python27\Lib\site-packages")
sys.path.append(r"\\isln-smb\thr3dcgi_config\Agnostic")

from shotgun_utils import project_util


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

        logging.info("Setting Global Variable for THR3d")

        entity = multi_launchapp.context.task
        if not entity:
            entity = multi_launchapp.context.entity

        if entity:

            type_ = entity.get('type')
            id_ = entity.get('id')
            filters = [['id', 'is', id_]]

            # find the current task info
            task = project_util.get_entity(filters=filters,
                                           entity_type=type_,
                                           find_="one")

            # Change the task's status
            result = project_util.set_status(task, 'ip')
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
            logging.info("app_path == > ", app_path)

        if multi_launchapp.get_setting("engine") == "tk-houdini":
            logging.info("Running Before Launch Functions for Houdini")
            os.environ["HOUDINI_USE_OTL_AS_DEFAULT_HDA_EXT"] = "1"
            os.environ["HOUDINI_OTLSCAN_PATH"] = r"\\isln-smb\thr3dcgi_config\Houdini\otl"

        if multi_launchapp.get_setting("engine") == "tk-maya":
            logging.info("Running Before Launch Functions for Maya")
            logging.info("Running Maya", version)
            logging.info("app_path == > ", app_path)
            logging.info("app_args == > ", app_args)
            logging.info("kwargs == > ", kwargs)
            logging.info("current_entity == > ", entity)
