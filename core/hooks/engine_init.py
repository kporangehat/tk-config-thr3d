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

# TODO: Once system added this to environment, use the following:
# sys.path.append(os.environ['THR3D_AGNOSTIC'])
sys.path.append(r'\\isln-smb\thr3dcgi_config\Agnostic')
from tk_utils import tk_utils
from config_utils import template_name


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

            # 4- Load the latest working file if it's found
            entity_name = engine.context.entity.get('name')
            task_name = engine.context.task.get('name')
            step = engine.context.step
            step_id = step.get('id')
            find_step = engine.sgtk.shotgun.find_one('Step',
                                                     filters=[['id', 'is',
                                                               step_id]],
                                                     fields=['short_name'])
            step_short_name = find_step.get('short_name')

            if step_short_name:
                if task_name not in template_name.DEFAULT_TASK_NAME:
                    step_short_name = task_name + "_" + step_short_name

                # Gathering all the work files
                all_working_files = engine.sgtk.paths_from_template(
                    engine.sgtk.templates["3d_asset_work_maya"],
                    engine.context.task)
                # Filter out the scene that are not related to this task
                context_files = []
                for p in all_working_files:
                    if entity_name in p and step_short_name in p:
                        context_files.append(p)
                # Get the latest version from all paths
                latest_file = tk_utils.latest_work_file(context_files,
                                                        engine.sgtk)
                # If the latest file exists, open the scene
                if latest_file:
                    file_name = os.path.basename(latest_file)
                    pm.inViewMessage(
                        amg='Loading the latest work file: '
                            '<hl>{}</hl> '.format(file_name),
                        pos='midCenter',
                        fade=True)
                    pm.openFile(latest_file, force=True)
                else:
                    logging.info("No working file was found "
                                 "for this Task to load")
            else:
                logging.info("Failed to find the latest work file since the "
                             "can't access the Step. "
                             "Step: {}".format(find_step))
