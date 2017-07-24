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

import time

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

from tank import Hook

from common import find_menu_item
from tk_utils import tk_file_handler
from maya_utils import load_utils as m_load_utils


class EngineInit(Hook):

    def execute(self, engine, **kwargs):
        """
        Gets executed when a Toolkit engine has fully initialized.
        At this point, all applications and frameworks have been loaded,
        and the engine is fully operational.
        """
        # Setting an global environment, this is being used during the
        # rendering of farm in Deadline
        os.environ['DIVISION'] = "THR3D"

        # Required variable
        step_name = None

        # Get context information
        try:
            step = engine.context.step
            step_id = step.get('id', None)
            find_step = engine.sgtk.shotgun.find_one('Step',
                                                     filters=[['id', 'is',
                                                               step_id]],
                                                     fields=['short_name',
                                                             'code'])
            step_name = find_step.get('code', None)

        except Exception as e:
            engine.log_debug("Engine Init Failed to load: {}".format(str(e)))
            pass

        # After Maya load do the following tasks
        if engine.name == "tk-maya":
            try:
                # 1- Load PyMel
                import pymel.core as pm
                logging.info("Imported PyMel as pm")

                # 2- Load V-ray
                vray = m_load_utils.load_plugin("vrayformaya")
                if vray:
                    # 3- Set the renderer to V-Ray
                    pm.setAttr("defaultRenderGlobals.currentRenderer",
                               "vray",
                               type="string")
                    logging.info("Setting V-ray as a renderer")
            except ImportError:
                pm = None
                logging.warning("Was not able to import PyMel.")

            # 4- Load the THR3D Menu
            menu_items = find_menu_item.find_commands(Agnostic.THR3D_MAYA)
            if menu_items:
                # Find/Create THR3D menu
                try:
                    pm.menu("THR3D", q=True, label=True)
                    logging.debug("THR3D menu already exists. Going to clear "
                                  "the menu items and re-populate it.")

                    pm.menu("THR3D", deleteAllItems=True, edit=True)
                except RuntimeError:
                    logging.debug("Creating the THR3D menu.")
                    pm.menu("THR3D",
                            label="THR3D",
                            parent=pm.melGlobals["gMainWindow"],
                            tearOff=True)
                # Add item to the menu
                for menu_item in menu_items:
                    menu = menu_items.get(menu_item)
                    command_env = menu.get('env')

                    # We don't want to load the Dev environment tools
                    if command_env == "dev":
                        continue

                    # We want to load the tools that are related to the
                    # current context
                    command_context = menu.get('context')
                    if step_name.lower() not in command_context:
                        continue

                    command_name = menu.get('command')
                    command_path = menu.get('path')
                    command_label = menu.get('label')

                    sys.path.append(command_path)
                    command = __import__(command_name)
                    pm.menuItem(command_name,
                                label=command_label,
                                parent="THR3D",
                                command=command.execute)
                    logging.info("Added {} command to the "
                                 "THR3D menu".format(command_label))

                # If there is no the THR3D menu has no item, delete it:
                if not pm.menu("THR3D", q=True, itemArray=True):
                    pm.deleteUI("THR3D")
                    logging.debug("No THR3D menu item was found, so the menu "
                                  "is deleted!")

            # 5- # Find and open the latest work file
            templates = ["3d_shot_work_maya", "3d_asset_work_maya"]
            latest_file = tk_file_handler.get_latest_scene_file(engine,
                                                                templates)

            if latest_file:
                file_name = os.path.basename(latest_file)
                engine.show_busy(
                    "Loading the latest work file:",
                    file_name
                )

                time.sleep(4)
                engine.clear_busy()

                pm.openFile(latest_file, force=True)

        elif engine.name == "tk-nuke":
            import nuke

            # Find and open the latest work file
            templates = ["2d_shot_work_nuke", "2d_asset_work_nuke"]
            latest_file = tk_file_handler.get_latest_scene_file(engine,
                                                                templates)
            if latest_file:
                file_name = os.path.basename(latest_file)
                for i in nuke.allNodes():
                    nuke.delete(i)

                nuke.nodePaste(latest_file)

                engine.show_busy(
                    "Loading the latest work file:",
                    file_name
                )

                time.sleep(3)
                engine.clear_busy()

        elif engine.name == "tk-photoshopcc" or engine.name == "tk-photoshop":

            # Find and open the latest work file
            templates = ["2d_shot_work_photoshop", "2d_asset_work_photoshop"]
            latest_file = tk_file_handler.get_latest_scene_file(engine,
                                                                templates)

            engine.log_info("Opening this: {}".format(latest_file))
            if latest_file:
                adobe = engine.adobe
                scene_file = adobe.File(latest_file)
                adobe.app.load(scene_file)
