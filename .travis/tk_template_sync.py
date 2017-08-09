# Copyright 2017 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license agreement
# provided at the time of installation or download, or which otherwise accompanies
# this software in either electronic or hard copy form.
#
#
"""
Syncs any changes from the master templates.yml file (THR3D - Birmingham) to other facility
template files. 
"""

import os
import logging
import argparse
from ruamel.yaml import YAML
import copy


# Ensure we have at least a default handler set
formatter = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)s] %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

_DESCRIPTION = """
This script syncs the master templates-d3d.yml file to all other facility template files.
These files should always be identical except for the defined root for each template. Since
each facility has the same filesystem structure, the template paths themselves will all be
the same at each facility. However, the structure will have a different mount point at each
facility. Therefore, we must define a root for each facility in Shotgun and Toolkit and 
have a templates file that utilizes the correct root for each facility.

Template files will all exist in config/core/templates/templates-<facility_code>.yml (for
example templates-STO.yml for Toronto).

The main config/core/templates.yml file that Toolkit relies on has a single include that 
resolves to the correct path using an environment variable %THR3D_FACILITY%
"""
FACILITY_STORAGES = {
    "D3D": {"primary": "primary", "secondary": "secondary"},
    "STO": {"primary": "STO-primary", "secondary": "STO-secondary"},
    }
MASTER_LOCATION = "D3D"


def get_template_path(config_path, facility):
    """
    Calculate the correct full path to the templates file for the given facility and 
    pipeline configuration.

    :param str config_path: Full path to the pipeline configuration.
    :param str facility: THR3D facility code eg. "D3D"
    :returns str: Full path to the facility's templates file for this pipeline configuration.
    """
    templates_filename = "templates-%s.yml" % facility
    if config_path:
        return os.path.join(config_path, "config", "core", "templates", templates_filename)
    else:
        return os.path.join("core", "templates", templates_filename)


def load_master_templates_file(config_path):
    """
    Load the master templates file for this configuration.

    :param str config_path: Full path to the pipeline configuration.
    :returns dict: Data structure loaded from the master templates yml file.
    :raises: UserWarning if the file does not exist or there was a problem loading it. 
    """
    # /path/to/pc/config/core/templates/templates-D3D.yml
    template_path = get_template_path(config_path, MASTER_LOCATION)
    
    yaml = YAML()
    try:
        with open(template_path, "r") as fh:
            raw_data = yaml.load(fh)
    except IOError:
        raise UserWarning("File does not exist: %s" % template_path)
    except Exception, e:
        raise UserWarning("Could not open file '%s'. Error reported: '%s'" % (template_path, e))
    
    logger.info("Loaded master templates file from %s" % template_path)
    return raw_data


def write_templates_file(config_path, facility, master_data):
    """
    Convert and write templates file in the pipeline configuration for the given facility.

    :param str config_path: Full path to the pipeline configuration.
    :param str facility: THR3D facility code eg. "D3D"
    :param dict master_data: Data structure loaded from the master templates yml file.
    :raises: UserWarning if there is a non-standard root name detected or there is an error
             writing the file to disk.
    """
    # Don't overwrite the master.
    if facility == MASTER_LOCATION:
        return

    logger.info("Converting master template data for %s" % facility)
    # Create new data structure 
    new_data = copy.deepcopy(master_data)
    for template_name, definition in new_data.get("paths").iteritems():
        logger.debug("%s: %s" % (template_name, definition))
        # If the root_name isn't specified, it's assumed to be "primary" but we also 
        # use it for @includes. We will assume for now that any definition that is a 
        # str and has no root_name defined is an @include and leave it as-is. 
        if isinstance(definition, basestring):
            logger.debug("Skipping %s as it looks like it defines an @include" % definition)
            continue
        if not definition.get("root_name") or "primary" in definition["root_name"]:
            definition["root_name"] = FACILITY_STORAGES[facility]["primary"]
        elif "secondary" in definition["root_name"]:
            definition["root_name"] = FACILITY_STORAGES[facility]["secondary"]
        else:
            # Be unforgiving if we find something we don't recognize. We only know
            # about primary and secondary as storage names and use these as flags.
            raise UserWarning("root_name for '%s' in the master templates file that doesn't "
                              "match 'primary' or 'secondary': %s" % (
                                template_name,
                                definition["root_name"]
                              ))

    # Write the file
    facility_template_path = get_template_path(config_path, facility)
    try:
        yaml = YAML()
        with open(facility_template_path, "w") as fh:
            yaml.dump(new_data, fh)
    except IOError as e:
        raise UserWarning("Unable to open facility templates file for writing (%s): %s" % (
            facility_template_path,
            e
        ))
    except Exception, e:
        raise UserWarning("An error occurred while writing facility templates file (%s): %s" % (
            facility_template_path, 
            e
        ))
    logger.info("[%s] Updated root storage definitions in %s" % (facility, facility_template_path))


def main(args=None):
    """
    Main entry point, parse args and sync files.
    :param list args: Optional list of arguments, fallback to sys.argv
    """
    parser = argparse.ArgumentParser(
        description="Sync master templates file to other facility template files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_DESCRIPTION
    )

    parser.add_argument("--config", action="store", dest="config_path",
                        help="Full path to pipeline config root")
    parser.add_argument("--debug", action="store_true", default=False)

    args = parser.parse_args(args)

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.info("Setting log level to DEBUG")
    else:
        logger.setLevel(logging.INFO)

    logger.info("Syncing facility templates files in %s" % args.config_path)
    # Load master templates file
    master_data = load_master_templates_file(args.config_path)
    
    # For each facility, write out a copy of the master file using
    # that facility's root.
    facilities = FACILITY_STORAGES.keys()
    for facility in facilities:
        write_templates_file(args.config_path, facility, master_data)

    logger.info("-"*40)
    logger.info("Complete!")
    logger.info(" ")


if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        logger.exception(e)





