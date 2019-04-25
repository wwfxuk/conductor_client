
import os
import re
# from itertools import takewhile
# import glob
LETTER_RE = re.compile(r'^([a-zA-Z]):')


class GPathError(Exception):
    pass


class Path(object):

    def __init__(self, path):
        """Initialize."""

        if not path:
            raise GPathError("Empty path")

        if isinstance(path, list):
            ipath = path[:]
            self._drive_letter = ipath.pop(0)[0] if LETTER_RE.match(ipath[0]) else None
            self._segments = ipath
        else:
            path = os.path.expanduser(os.path.expandvars(path))

            match = LETTER_RE.match(path)
            self._drive_letter = match.group(1) if match else None
            remainder = re.sub(LETTER_RE, "", path)

            if remainder[0] not in ["/", "\\"]:
                raise GPathError("Not an absolute path")

            # add more bad characters here, but be aware
            # some glob and expansion characters are valid
            if any((c in [":"]) for c in remainder):
                raise GPathError("Bad characters in path")

            self._segments = [s for s in re.split('/|\\\\', remainder) if s]

        self._depth = len(self._segments)


       
    def _construct_path(self, sep, with_drive_letter=True):
        result = "{}{}".format(sep, sep.join(self._segments))
        if with_drive_letter and self._drive_letter:
            result = "{}:{}".format(self._drive_letter, result)
        return result

    def posix_path(self, with_drive_letter=True):
        return self._construct_path("/", with_drive_letter)

    def windows_path(self, with_drive_letter=True):
        return self._construct_path("\\", with_drive_letter)

    def os_path(self, with_drive_letter=True):
        if os.name == "nt":
            return self.windows_path(with_drive_letter)
        return self.posix_path(with_drive_letter)



    def startswith(self, path):
        return self.posix_path().startswith(path.posix_path()) 

    def __len__(self):
        return len(self.posix_path())

    def __eq__(self, rhs): 
        if not isinstance(rhs, Path):
            raise NotImplementedError
        return self.posix_path() == rhs.posix_path()

    def __ne__(self, rhs): 
        return not self == rhs

    @property
    def depth(self):
        return self._depth

    @property
    def drive_letter(self):
        return self._drive_letter or ""
    
    @property
    def segments(self):
        return self._segments or []
    
    @property
    def all_components(self):
        if self.drive_letter:
            return [ "{}:".format(self.drive_letter)] + self.segments
        else:
            return self.segments

    @property
    def tail(self):
        return self._segments[-1]


    # def __str__(self):
    #     """Path in the current os."""
    #     progs = Progression.factory(self._iterable)
    #     return (',').join([str(p) for p in progs])

    # def add(self, *files, **kw):
    #     """Add one or more files.

    #     Files will be added according to the must_exist check. Duplicate
    #     files and directories that contain other files may be added and
    #     no deduplication will happen at this time.
    #     """
    #     must_exist = kw.get("must_exist", True)
    #     for file in files:
    #         self._add_a_file(file, must_exist)

    # def _deduplicate(self):
    #     """Deduplicate if it has become dirty.

    #     Algorithm explained at:
    #     https://stackoverflow.com/questions/49478361 .
    #     """
    #     if self._clean:
    #         return

    #     sorted_entries = sorted(
    #         self._entries, key=lambda entry: (
    #             entry.count(
    #                 os.sep), -len(entry)))
    #     self._entries = []
    #     for entry in sorted_entries:
    #         if any(entry.startswith(p) for p in self._entries):
    #             continue
    #         self._entries.append(entry)
    #     self._clean = True

    # def _add_a_file(self, f, must_exist):
    #     """Add a single file.

    #     If necessary, expand the user, expand env vars, and get the abs
    #     path. Note that when an element is added, it may cause the list
    #     to change next time it is deduplicated, which includes getting
    #     shorter. This could happen if a containing directory is added.
    #     Therefore we have to set the peg position to zero.
    #     """
    #     f = os.path.abspath(
    #         os.path.expanduser(
    #             os.path.expandvars(f)))
    #     if not must_exist or os.path.exists(f):
    #         self._entries.append(f)
    #         self._clean = False
    #     self._current = 0

    # def common_path(self):
    #     """Find the common path among entries.

    #     This is useful for determining output directory when many
    #     renders are rendering to different places.

    #     In the case where
    #     only single path exists, it is not possible to tell from its
    #     name whether it is a file or directory. We don't want this
    #     method to touch the filesystem, that should be someone else's
    #     problem. A trailing slash would be a hint, but the absence of a
    #     trailing slash does not mean its a regular file. Therefore, in
    #     the case of a single file we return it AS-IS and the caller can
    #     then stat to find out for sure.

    #     If no files exist return None.

    #     If the filesystem root is the common path, return os.sep.
    #     """
    #     if not self._entries:
    #         return None

    #     def _all_the_same(rhs):
    #         return all(n == rhs[0] for n in rhs[1:])
    #     levels = zip(*[p.split(os.sep) for p in self._entries])
    #     return os.sep.join(
    #         x[0] for x in takewhile(
    #             _all_the_same, levels)) or os.sep

    # def glob(self):
    #     self._deduplicate()
    #     globbed = []
    #     for entry in self._entries:
    #         globbed += glob.glob(entry)
    #     self._entries = globbed
    #     self._clean = False
    #     self._current = 0

    # def __iter__(self):
    #     """Get an iterator to entries.

    #     Deduplicate just in time.
    #     """
    #     self._deduplicate()
    #     return iter(self._entries)

    # def next(self):
    #     """Get the next element.

    #     Deduplicate just in time.
    #     """
    #     self._deduplicate()
    #     if self._current >= len(self._entries):
    #         raise StopIteration
    #     else:
    #         prev = self._current
    #         self._current += 1
    #         return self._entries[prev]

    # def __len__(self):
    #     """Get the size of the entry list.

    #     Deduplicate just in time.
    #     """
    #     self._deduplicate()
    #     return len(self._entries)
