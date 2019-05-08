import os
import ix
from conductor.native.lib.data_block import ConductorDataBlock
from conductor.clarisse.clarisse_info import ClarisseInfo
from conductor.clarisse.scripted_class import (
    frames_ui, instances_ui, projects_ui)




DEFAULT_CMD_EXPRESSION = """
cmd = "bash -c 'mkdir -p ";
cmd += $CT_DIRECTORIES;
cmd += " && cnode ";
cmd += $CT_RENDER_PACKAGE;
cmd += "  -log_level Debug5  -image ";
cmd += $CT_SOURCES;
cmd += " -image_frames_list ";
cmd += $CT_CHUNKS;
cmd += "'";
cmd"""

if os.name == "nt":
    DEFAULT_CMD_EXPRESSION = """
cmd = "bash -c 'mkdir -p ";
cmd += $CT_DIRECTORIES;
cmd += " && cnode ";
cmd += $CT_RENDER_PACKAGE;
cmd += " -script ";
cmd += $CT_SCRIPT_DIR;
cmd += "/ct_windows_prep.py";
cmd += " -log_level Debug5  -image ";
cmd += $CT_SOURCES;
cmd += " -image_frames_list ";
cmd += $CT_CHUNKS;
cmd += "'";
cmd"""


def force_ae_refresh(node):
    """Trigger an attribute editor refresh.

    The only way to force the attribute editor to refresh, it seems, is
    to remove and replace a preset in a long type attribute.
    """
    attr = node.get_attribute("instance_type")
    count = attr.get_preset_count()
    applied = attr.get_applied_preset_index()
    if count:
        last = count - 1
        preset = (
            attr.get_preset_label(last),
            attr.get_preset_value(last)
        )
        attr.remove_preset(last)
        attr.add_preset(preset[0], preset[1])
        attr.set_long(applied)


staticmethod
def refresh(_, **kw):
    """Respond to do_setup button click.

    Update UI for projects and instances from the data block. kwargs may
    contain the force keyword, which will invalidate the datablock and
    fetch fresh from Conductor. We may as well update all ConductorJob
    nodes.
    """
    kw["product"] = "clarisse"
    data_block = ConductorDataBlock(**kw)
    nodes = ix.api.OfObjectArray()
    ix.application.get_factory().get_all_objects("ConductorJob", nodes)

    host = ClarisseInfo().get()
    detected_host_paths = data_block.package_tree().get_all_paths_to(
        **host)

    for obj in nodes:

        projects_ui.update(obj, data_block)
        instances_ui.update(obj, data_block)
        frames_ui.update_frame_stats_message(obj)

        title_attr = obj.get_attribute("title")
        if not title_attr.get_string():
            title_attr.set_expression(
                '"Clarisse: "+$CT_JOB+" "+$CT_SEQUENCE')

        task_template_attr = obj.get_attribute("task_template")
        if not task_template_attr.get_string():

            task_template_attr.set_expression(DEFAULT_CMD_EXPRESSION)
        task_template_attr.set_locked(True)

        packages_attr = obj.get_attribute("packages")
        if not packages_attr.get_value_count():
            for path in detected_host_paths:
                print detected_host_paths
                packages_attr.add_string(path)

        inst_type_attr = obj.get_attribute("instance_type")
        # if not inst_type_attr.get_long():
        #     inst_type_attr.set_long(0)

        project_attr = obj.get_attribute("project")
        # if not project_attr.get_long():
        #     project_attr.set_long(0)
