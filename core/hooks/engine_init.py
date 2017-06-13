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
Hook that gets executed every time an engine has fully initialized.

"""

import os
import sys
import logging

from tank import Hook


class EngineInit(Hook):

    def execute(self, engine, **kwargs):
        """
        Gets executed when a Toolkit engine has fully initialized.
        At this point, all applications and frameworks have been loaded,
        and the engine is fully operational.
        """
        # Setting an global environment
        os.environ['DIVISION'] = "THR3D"

        # After Maya load do the following tasks
        if engine.name == "tk-maya":
            try:
                # 1- Load PyMel
                import pymel.core as pm
                logging.info("Imported PyMel as pm")
                plugs = pm.pluginInfo(query=True, listPlugins=True)
                try:
                    # 2- Load V-ray
                    if "vrayformaya" not in plugs:
                        pm.loadPlugin('vrayformaya', quiet=True)
                        logging.info("Loaded V-ray Plugin")
                    # 3- Set the renderer to V-Ray
                    pm.setAttr("defaultRenderGlobals.currentRenderer",
                               "vray",
                               type="string")
                except Exception as e:
                    logging.warning("Was not able to lead V-ray "
                                    "Plugin.\n{}".format(str(e)))
            except ImportError:
                logging.warning("Was not able to import PyMel.")
