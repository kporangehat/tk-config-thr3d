"""
Time log punch out
"""

import os
import sys
import logging
import tank

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

try:
    from sgtk.platform.qt import QtGui, QtCore
except ImportError:
    from PySide import QtGui, QtCore

from shotgun_utils import time_log_utils


class BeforeAppLaunch(tank.Hook):
    """
    Hook to set up the system prior to app launch.
    """

    def execute(self, app_path, app_args, version, **kwargs):

        logging.info("Setting Up for THR3D Pipeline")

        # accessing the current context (current shot, etc)
        # can be done via the parent object
        multi_launchapp = self.parent

        user_entity = multi_launchapp.context.user
        task_entity = multi_launchapp.context.task

        if task_entity:

            msg_box = QtGui.QMessageBox()
            msg_box.setMinimumWidth(500)
            msg_box.setText("Punching Out?")
            msg_box.setInformativeText("Do you wanna continue with "
                                       "punch out | Task ID"
                                       ": {}".format(task_entity.get('id')))
            msg_box.setStandardButtons(QtGui.QMessageBox.Ok |
                                       QtGui.QMessageBox.Cancel)
            ret = msg_box.exec_()

            if ret == QtGui.QMessageBox.Ok:
                # Start time logging
                time_log_utils.stop_timelog_clock(task=task_entity,
                                                  user=user_entity)
