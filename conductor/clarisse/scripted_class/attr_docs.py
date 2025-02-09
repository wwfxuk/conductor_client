"""
Module is responsible for providing documentation for all attributes of the scripted class.
"""


def set_docs(s_class):

    s_class.set_attr_doc(
        "connect",
        """Connects to Conductor and updates available projects and machine types. Sign in may be required. Also sets empty string attributes to their defaults.""",
    )

    s_class.set_attr_doc(
        "preflight",
        """Build a submission as json and inspect it before submitting to Conductor.""",
    )

    s_class.set_attr_doc("submit", """Submits this job to Conductor.""")

    s_class.set_attr_doc(
        "title",
        """Sets the title that appears in the Conductor dashboard. You may use Clarisse variables and some Conductor tokens to construct the title.""",
    )

    s_class.set_attr_doc(
        "images_and_layers",
        """Sets the items to be rendered. Images or Layers must have their Render to Disk attribute set. The Save As field must contain a filename.""",
    )

    s_class.set_attr_doc("conductor_project_name", """Sets the Conductor project.""")

    s_class.set_attr_doc(
        "use_custom_frames",
        """Overrides the frame ranges from connected image nodes.""",
    )

    s_class.set_attr_doc(
        "custom_frames",
        """Specifies a set of frames to render. Provide a comma-separated list of progressions. Example 1,7,10-20,30-60x3,1001.""",
    )

    s_class.set_attr_doc("chunk_size", """Sets the number of frames per task.""")

    s_class.set_attr_doc(
        "best_chunk_size",
        """Tries to adjust the chunk size so that frames are evenly distributed among the current number of tasks.""",
    )

    s_class.set_attr_doc("use_scout_frames", """Activates a set of frames to scout.""")

    s_class.set_attr_doc(
        "scout_frames",
        """Scout-frames to render. Tasks containing any of the specified scout frames, are run in their entirety. Other frames are set to a holding state.""",
    )

    s_class.set_attr_doc(
        "tiles", """Render tiles. Split each single frame across many machines."""
    )

    s_class.set_attr_doc(
        "preemptible",
        """Activates use of low-cost instances. Premptble instances may be stopped at any time by the cloud provider. See the Conductor documentation site for a discussion of the situations where preemptible instances are suitable.""",
    )

    s_class.set_attr_doc(
        "instance_type", """Specifies the required hardware configuration."""
    )

    s_class.set_attr_doc(
        "retries",
        """Sets the number of times to retry a failed task before marking it failed.""",
    )

    s_class.set_attr_doc(
        "dependency_scan_policy",
        """Specifies how to search the project for references to files it depends on. The Smart Sequence option tries to identify only those files that are needed for the specified frames. The Glob option finds any files that match a hash pattern. If you have saved all required files in the cached upload list, you can set the policy to No Scan.""",
    )

    s_class.set_attr_doc(
        "local_upload",
        """Uploads files from your workstation, as opposed to using an upload daemon.""",
    )

    s_class.set_attr_doc(
        "force_upload",
        """Forces files to be uploaded, even if they already exist at Conductor.""",
    )

    s_class.set_attr_doc(
        "upload_only", """Uploads files but does not start any tasks."""
    )

    s_class.set_attr_doc(
        "manage_extra_uploads",
        """Opens a panel to browse or scan for files to upload. If any files are not found by the dependency scan at submission time, they may be added here.""",
    )

    s_class.set_attr_doc(
        "extra_uploads",
        """Files to uploaded in addition to any files found by dependency scanning.""",
    )

    s_class.set_attr_doc(
        "clarisse_version",
        """Choose the version of Clarisse to run on the render nodes.""",
    )

    s_class.set_attr_doc(
        "manage_extra_environment",
        """Opens a panel for making modifications to the remote environment.""",
    )

    s_class.set_attr_doc(
        "extra_environment", """Extra environment encoded as a JSON string."""
    )

    s_class.set_attr_doc(
        "task_template",
        """Specifies a template for the command that will be run on remote instances. See the Conductor documentation site for a detailed discussion.""",
    )

    s_class.set_attr_doc(
        "localize_contexts",
        """Localize contexts before dispatching to Conductor. This will cause your project to be saved and then reloaded after submission, which may take a long time for large projects.""",
    )

    s_class.set_attr_doc(
        "timestamp_render_package",
        """Add a timestamp to the project filename that will be submitted.""",
    )

    s_class.set_attr_doc(
        "clean_up_render_package",
        """Removes the render project file after submission.""",
    )

    s_class.set_attr_doc(
        "notify",
        """Indicates that notifications will be sent by email on job completion.""",
    )

    s_class.set_attr_doc(
        "email_addresses",
        """A comma delimited list of emails addresses to notify on job completion.""",
    )

    s_class.set_attr_doc(
        "show_tracebacks", """Shows a stacktrace when something goes wrong."""
    )

    s_class.set_attr_doc(
        "conductor_log_level",
        """Sets the severity above which Conductor's logging emits messages.""",
    )
