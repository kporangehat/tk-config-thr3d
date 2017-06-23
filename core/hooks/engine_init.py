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

from config_utils import template_name
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
        # Setting an global environment
        os.environ['DIVISION'] = "THR3D"

        # After Maya load do the following tasks
        if engine.name == "tk-maya":
            # Get context information
            entity_name = engine.context.entity.get('name')
            task_name = engine.context.task.get('name')
            step = engine.context.step
            step_id = step.get('id')
            find_step = engine.sgtk.shotgun.find_one('Step',
                                                     filters=[['id', 'is',
                                                               step_id]],
                                                     fields=['short_name'])
            step_short_name = find_step.get('short_name')
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
                    command_name = menu.get('command')
                    command_path = menu.get('path')
                    command_label = menu.get('label')

                    sys.path.append(command_path)
                    command = __import__(command_name)
                    pm.menuItem(command_name,
                                label=command_label,
                                parent="THR3D",
                                command=command.execute)

            # 5- Load the latest working file if it's found
            if step_short_name:
                if task_name not in template_name.DEFAULT_TASK_NAME:
                    step_short_name = task_name + "_" + step_short_name

                # Gathering all the work files
                work_files = tk_file_handler.get_files("3d_shot_work_maya",
                                                       engine.context.entity,
                                                       engine.sgtk)
                work_files += tk_file_handler.get_files("3d_asset_work_maya",
                                                        engine.context.entity,
                                                        engine.sgtk)

                # Filter out the scene that are not related to this task
                context_files = []
                for p in work_files:
                    if entity_name in p and step_short_name in p:
                        context_files.append(p)
                # Get the latest version from all paths
                if context_files:
                    latest_file = sorted(context_files)[-1]

                    if os.path.exists(latest_file):
                        file_name = os.path.basename(latest_file)
                        pm.inViewMessage(
                            amg='Loading the latest work file: '
                                '<hl>{}</hl> '.format(file_name),
                            pos='midCenter',
                            fade=True)
                        pm.openFile(latest_file, force=True)
                    else:
                        logging.info("The working file was not found on "
                                     "disk: {}".format(latest_file))
                else:
                    logging.info("No working file was found "
                                 "for this Task to load")
            else:
                logging.info("Failed to find the latest work file since the "
                             "can't access the Step. "
                             "Step: {}".format(find_step))
