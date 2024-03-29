#!/usr/bin/python

#-------------------------------------------------------------------------------
# supports:     python 2.6, 2.7
#               python 3.3 (or newer)
#
# author:       dawid.koszewski.01@gmail.com
# date:         2019.10.30
# update:       2021.05.13
# version:      02f 5Gedition
#
# written in Notepad++
#-------------------------------------------------------------------------------


################# KNOWN ISSUES: #################
# - no possibility to install requests module on wrlinb (module is needed to download Stratix from artifactory)


# please don't be afraid of this script
# the main function is located at the very bottom - take a look at it first - everything will become clear


#===============================================================================
# import section
#===============================================================================

#from __builtin__ import open as bltn_open      #imported below in try except block
import copy
import errno
import io
import os
import random
import re
#import requests    #imported below in isFileAvailable and getFileFromArtifactory functions
import shutil
import stat
import struct
import subprocess
import sys
import tarfile
import time
#import zlib        #imported below in try except block

#import inspect #inspect.currentframe().f_code.co_name #(python version of c++ __PRETTY_FUNCTION__)

#-------------------------------------------------------------------------------


#===============================================================================
# helper functions needed for import handling and also used throughout the code
#===============================================================================

def pressEnterToExit():
#1.
    # try:
        # raw_input("\nPress Enter to exit...\n") #python2 only
    # except (SyntaxError, Exception) as e:
        # input("\nPress Enter to exit...\n") #python3 only
#2.
    try:
        input("\nPress Enter to exit...\n") #python3 only
    except (SyntaxError, Exception) as e:
        pass
    time.sleep(1)
    sys.exit()


def pressEnterToContinue():
#1.
    # try:
        # raw_input("\nPress Enter to continue...\n") #python2 only
    # except (SyntaxError, Exception) as e:
        # input("\nPress Enter to continue...\n") #python3 only
#2.
    try:
        input("\nPress Enter to continue...\n")  #python3 only
    except (SyntaxError, Exception) as e:
        pass
    time.sleep(1)

#-------------------------------------------------------------------------------


#===============================================================================
# further import handling
#===============================================================================

try:
    from __builtin__ import open as bltn_open #python2 only
except (SyntaxError, Exception) as e:
    from builtins import open as bltn_open #python3 only


def installRequests():
    try:
        print("If the following command will fail, script will try to access pypi.org through a proxy:")
        print("pip install requests --retries 0 --timeout 3")
        print("Please wait for up to 15 seconds...")
        subprocess.check_call("pip install requests --retries 0 --timeout 3")
    except (subprocess.CalledProcessError, Exception) as e:
        print("\ninstallRequests(e1) %s\n" % e)
        try:
            print("pip install requests --proxy defra1c-proxy.emea.nsn-net.net:8080 --retries 0 --timeout 3")
            print("Please wait for up to 15 seconds...")
            subprocess.check_call("pip install requests --proxy defra1c-proxy.emea.nsn-net.net:8080 --retries 0 --timeout 3")
        except (subprocess.CalledProcessError, Exception) as e:
            print("\ninstallRequests(e2) %s\n" % e)
            try:
                print("pip install requests --proxy fihel1d-proxy.emea.nsn-net.net:8080 --retries 0 --timeout 3")
                print("Please wait for up to 15 seconds...")
                subprocess.check_call("pip install requests --proxy fihel1d-proxy.emea.nsn-net.net:8080 --retries 0 --timeout 3")
            except (subprocess.CalledProcessError, Exception) as e:
                print("\ninstallRequests(e3) %s\n" % e)
                pass
    pressEnterToContinue()

#-------------------------------------------------------------------------------


#===============================================================================
# python version global variables
#===============================================================================

PYTHON_MAJOR = sys.version_info[0]
PYTHON_MINOR = sys.version_info[1]
PYTHON_PATCH = sys.version_info[2]

def printDetectedAndSupportedPythonVersion():
    if((PYTHON_MAJOR == 2 and PYTHON_MINOR == 6 and PYTHON_PATCH >= 6)
    or (PYTHON_MAJOR == 2 and PYTHON_MINOR == 7 and PYTHON_PATCH >= 4)
    or (PYTHON_MAJOR == 3 and PYTHON_MINOR == 3 and PYTHON_PATCH >= 5)
    or (PYTHON_MAJOR == 3 and PYTHON_MINOR == 4 and PYTHON_PATCH >= 5)
    or (PYTHON_MAJOR == 3 and PYTHON_MINOR == 5 and PYTHON_PATCH >= 2)
    or (PYTHON_MAJOR == 3 and PYTHON_MINOR >= 6)):
        print("\ndetected python version: %d.%d.%d [SUPPORTED]\n(tested in 2.6.6, 2.7.4, 3.3.5, 3.8.0)" % (PYTHON_MAJOR, PYTHON_MINOR, PYTHON_PATCH))
    elif (PYTHON_MAJOR >= 4):
        print("\ndetected python version: %d.%d.%d [PROBABLY SUPPORTED]\n(tested in 2.6.6, 2.7.4, 3.3.5, 3.8.0)" % (PYTHON_MAJOR, PYTHON_MINOR, PYTHON_PATCH))
    else:
        print("\ndetected python version: %d.%d.%d [NOT TESTED]\n(it is highly recommended to upgrade to 2.6.6, 2.7.4, 3.3.5, 3.8.0 or any newer)" % (PYTHON_MAJOR, PYTHON_MINOR, PYTHON_PATCH))
    print("please do not hesitate to contact: dawid.koszewski.01@gmail.com\n")

printDetectedAndSupportedPythonVersion()

#-------------------------------------------------------------------------------


#===============================================================================
# python implementation of zlib.adler32 library
#===============================================================================

def adler32(buffer, checksum): #probably the Fastest pure Python Adler32 in the West (FPAW)
    sum2 = (checksum >> 16) & 0xffff;
    adler = checksum & 0xffff;

    # step = 256 #256 max for adler-=65521 version (256*255+1 = 65281 so adler modulo can be skipped)
    # i = 0
    buffer = bytearray(buffer)
    for byte in buffer:
        adler += byte
        sum2 += adler
        # i += 1
        # if i>= step:
            # # if adler >= 65521:
                # # adler -= 65521
            # adler %= 65521
            # sum2 %= 65521
            # i = 0
    # # if adler >= 65521:
        # # adler -= 65521
    adler %= 65521
    sum2 %= 65521

    return (sum2 << 16) | adler


def adler32_naive(buffer, checksum):
    sum2 = (checksum >> 16) & 0xffff;
    adler = checksum & 0xffff;
    buffer = bytearray(buffer)
    for byte in buffer:
        adler = (adler + byte) % 65521
        sum2 = (sum2 + adler) % 65521
    return (sum2 << 16) | adler


adler32_function = adler32

try:
    import zlib
    adler32_function = zlib.adler32
except (ImportError, Exception) as e:
    print("\nWARNING: %s\nscript will use python implementation of adler32 algorithm..." % e)
    adler32_function = adler32

#-------------------------------------------------------------------------------


################################################################################
#                                                                              #
# This is only a part of SHUTIL LIBRARY - needed to enable progress bar.       #
#                                                                              #
# contributors: gvanrossum, serhiy-storchaka, birkenfeld, pitrou, benjaminp,   #
#               rhettinger, merwok, loewis, tim-one, nnorwitz, doerwalter,     #
#               ronaldoussoren, ned-deily, florentx, freddrake, csernazs,      #
#               brettcannon, warsaw                                            #
#                                                                              #
# date:         24 Oct 2018                                                    #
# link:         https://github.com/python/cpython/blob/2.7/Lib/shutil.py       #
#                                                                              #
################################################################################

"""Utility functions for copying and archiving files and directory trees.

XXX The functions here don't copy the resource fork or other metadata on Mac.

"""

def _samefile(src, dst):
    # Macintosh, Unix.
    if hasattr(os.path, 'samefile'):
        try:
            return os.path.samefile(src, dst)
        except OSError:
            return False

    # All other platforms: check for same pathname.
    return (os.path.normcase(os.path.abspath(src)) ==
            os.path.normcase(os.path.abspath(dst)))


def copyfile(src, dst):
    """Copy data from src to dst"""
    if _samefile(src, dst):
        raise Error("`%s` and `%s` are the same file" % (src, dst))

    for fn in [src, dst]:
        try:
            st = os.stat(fn)
        except OSError:
            # File most likely does not exist
            pass
        else:
            # XXX What about other special files? (sockets, devices...)
            if stat.S_ISFIFO(st.st_mode):
                raise SpecialFileError("`%s` is a named pipe" % fn)

    #modified by dawid.koszewski.01@gmail.com
    try:
        fsrc = open(src, 'rb')
        try:
            fdst = open(dst, 'wb')
            try:
                #copyfileobj(fsrc, fdst)
                copyfileobj(fsrc, fdst, src)
                fdst.close()
            except (OSError, IOError) as e:
                print("\nFile copy ERROR: copyfile(e1) %s - %s" % (e.filename, e.strerror))
                pressEnterToExit()
            finally:
                fdst.close()
                fsrc.close()
        except (Exception) as e:
            print("\nFile copy ERROR: copyfile(e2) %s" % (e))
            pressEnterToExit()
        fsrc.close()
    except (Exception) as e:
        print("\nFile copy ERROR: copyfile(e3) %s" % (e))
        pressEnterToExit()


def copystat(src, dst):
    """Copy file metadata

    Copy the permission bits, last access time, last modification time, and
    flags from `src` to `dst`. On Linux, copystat() also copies the "extended
    attributes" where possible. The file contents, owner, and group are
    unaffected. `src` and `dst` are path names given as strings.
    """
    st = os.stat(src)
    mode = stat.S_IMODE(st.st_mode)
    if hasattr(os, 'utime'):
        os.utime(dst, (st.st_atime, st.st_mtime))
    if hasattr(os, 'chmod'):
        os.chmod(dst, mode)
    if hasattr(os, 'chflags') and hasattr(st, 'st_flags'):
        try:
            os.chflags(dst, st.st_flags)
        #except OSError, why:
        except OSError as why: #modified by dawid.koszewski.01@gmail.com
            for err in 'EOPNOTSUPP', 'ENOTSUP':
                if hasattr(errno, err) and why.errno == getattr(errno, err):
                    break
            else:
                raise


def copy2(src, dst):
    """Copy data and metadata. Return the file's destination.

    Metadata is copied with copystat(). Please see the copystat function
    for more information.

    The destination may be a directory.

    """
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    copyfile(src, dst)
    copystat(src, dst)

#-------------------------------------------------------------------------------


################################################################################
#                                                                              #
# This is only a PART of TARFILE LIBRARY - needed to CHECK TAR file INTEGRITY. #
# It contains PATCH TO BUG present in python 2.6, 2.7, 3.4, 3.5.               #
#                                                                              #
# The bug allowed to extract corrupted tar file without raising any errors     #
# (regardless of errorlevel setting).                                          #
#                                                                              #
# There are two versions used by this script - for python 2.* and 3.0-3.5.     #
# Below you can find version used by this script for python [ 2.* ].           #
#                                                                              #
# link to discussion:       https://bugs.python.org/issue24259                 #
# link to patch:            https://hg.python.org/cpython/rev/372aa98eb72e     #
#                                                                              #
# contributors: gustaebel, loewis, birkenfeld, nnorwitz, serhiy-storchaka,     #
#               tim-one, akuchling, orsenthil, jackjansen, rhettinger,         #
#               brettcannon, vadmium, ronaldoussoren, pjenvey, gvanrossum,     #
#               ezio-melotti, mdickinson, benjaminp, asvetlov                  #
#                                                                              #
# date:         30 Oct 2016                                                    #
# link:         https://github.com/python/cpython/blob/2.7/Lib/tarfile.py      #
#                                                                              #
################################################################################

#-------------------------------------------------------------------
# tarfile.py   [[[   branch 2.7   ]]] - used in this script for python 2.*
#-------------------------------------------------------------------
# Copyright (C) 2002 Lars Gustaebel <lars@gustaebel.de>
# All rights reserved.
#
# Permission  is  hereby granted,  free  of charge,  to  any person
# obtaining a  copy of  this software  and associated documentation
# files  (the  "Software"),  to   deal  in  the  Software   without
# restriction,  including  without limitation  the  rights to  use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies  of  the  Software,  and to  permit  persons  to  whom the
# Software  is  furnished  to  do  so,  subject  to  the  following
# conditions:
#
# The above copyright  notice and this  permission notice shall  be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS  IS", WITHOUT WARRANTY OF ANY  KIND,
# EXPRESS OR IMPLIED, INCLUDING  BUT NOT LIMITED TO  THE WARRANTIES
# OF  MERCHANTABILITY,  FITNESS   FOR  A  PARTICULAR   PURPOSE  AND
# NONINFRINGEMENT.  IN  NO  EVENT SHALL  THE  AUTHORS  OR COPYRIGHT
# HOLDERS  BE LIABLE  FOR ANY  CLAIM, DAMAGES  OR OTHER  LIABILITY,
# WHETHER  IN AN  ACTION OF  CONTRACT, TORT  OR OTHERWISE,  ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
"""Read from and write to tar format archives.
"""

__version__ = "$Revision: 85213 $"
# $Source$

version     = "0.9.0"
__author__  = "Lars Gustaebel (lars@gustaebel.de)"
__date__    = "$Date$"
__cvsid__   = "$Id$"
__credits__ = "Gustavo Niemeyer, Niels Gustaebel, Richard Townsend."

#---------------------------------------------------------
# tar constants
#---------------------------------------------------------
NUL = b"\0"                     # the null character
BLOCKSIZE = 512                 # length of processing blocks
RECORDSIZE = BLOCKSIZE * 20     # length of records
GNU_MAGIC = b"ustar  \0"        # magic gnu tar string
POSIX_MAGIC = b"ustar\x0000"    # magic posix tar string

LENGTH_NAME = 100               # maximum length of a filename
LENGTH_LINK = 100               # maximum length of a linkname
LENGTH_PREFIX = 155             # maximum length of the prefix field

REGTYPE = b"0"                  # regular file
AREGTYPE = b"\0"                # regular file
LNKTYPE = b"1"                  # link (inside TarFile)
SYMTYPE = b"2"                  # symbolic link
CHRTYPE = b"3"                  # character special device
BLKTYPE = b"4"                  # block special device
DIRTYPE = b"5"                  # directory
FIFOTYPE = b"6"                 # fifo special device
CONTTYPE = b"7"                 # contiguous file

GNUTYPE_LONGNAME = b"L"         # GNU tar longname
GNUTYPE_LONGLINK = b"K"         # GNU tar longlink
GNUTYPE_SPARSE = b"S"           # GNU tar sparse file

XHDTYPE = b"x"                  # POSIX.1-2001 extended header
XGLTYPE = b"g"                  # POSIX.1-2001 global header
SOLARIS_XHDTYPE = b"X"          # Solaris extended header

USTAR_FORMAT = 0                # POSIX.1-1988 (ustar) format
GNU_FORMAT = 1                  # GNU tar format
PAX_FORMAT = 2                  # POSIX.1-2001 (pax) format
DEFAULT_FORMAT = GNU_FORMAT

#---------------------------------------------------------
# TarFile constants
#---------------------------------------------------------
# File types that TarFile supports:
SUPPORTED_TYPES = (REGTYPE, AREGTYPE, LNKTYPE,
                   SYMTYPE, DIRTYPE, FIFOTYPE,
                   CONTTYPE, CHRTYPE, BLKTYPE,
                   GNUTYPE_LONGNAME, GNUTYPE_LONGLINK,
                   GNUTYPE_SPARSE)

# File types that will be treated as a regular file.
REGULAR_TYPES = (REGTYPE, AREGTYPE,
                 CONTTYPE, GNUTYPE_SPARSE)

# File types that are part of the GNU tar format.
GNU_TYPES = (GNUTYPE_LONGNAME, GNUTYPE_LONGLINK,
             GNUTYPE_SPARSE)

# Fields from a pax header that override a TarInfo3 attribute.
PAX_FIELDS = ("path", "linkpath", "size", "mtime",
              "uid", "gid", "uname", "gname")

# Fields from a pax header that are affected by hdrcharset.
#PAX_NAME_FIELDS = {"path", "linkpath", "uname", "gname"}
PAX_NAME_FIELDS = ("path", "linkpath", "uname", "gname")

# Fields in a pax header that are numbers, all other fields
# are treated as strings.
PAX_NUMBER_FIELDS = {
    "atime": float,
    "ctime": float,
    "mtime": float,
    "uid": int,
    "gid": int,
    "size": int
}

#---------------------------------------------------------
# initialization
#---------------------------------------------------------
# if os.name in ("nt", "ce"):
ENCODING = "utf-8"
# else:
    # ENCODING = sys.getfilesystemencoding()

#---------------------------------------------------------
# Some useful functions
#---------------------------------------------------------
def stn(s, length):
    """Convert a python string to a null-terminated string buffer.
    """
    return s[:length] + (length - len(s)) * NUL

def nts(s):
    """Convert a null-terminated string field to a python string.
    """
    # Use the string up to the first null char.
    p = s.find("\0")
    if p == -1:
        return s
    return s[:p]

def nti(s):
    """Convert a number field to a python number.
    """
    # There are two possible encodings for a number field, see
    # itn() below.
    if s[0] != chr(0o200):
        try:
            n = int(nts(s).strip() or "0", 8)
        except ValueError:
            raise InvalidHeaderError("invalid header")
    else:
        n = long(0)
        for i in xrange(len(s) - 1):
            n <<= 8
            n += ord(s[i + 1])
    return n


def uts(s, encoding, errors):
    """Convert a unicode object to a string.
    """
    if errors == "utf-8":
        # An extra error handler similar to the -o invalid=UTF-8 option
        # in POSIX.1-2001. Replace untranslatable characters with their
        # UTF-8 representation.
        try:
            return s.encode(encoding, "strict")
        except UnicodeEncodeError:
            x = []
            for c in s:
                try:
                    x.append(c.encode(encoding, "strict"))
                except UnicodeEncodeError:
                    x.append(c.encode("utf8"))
            return "".join(x)
    else:
        return s.encode(encoding, errors)

def calc_chksums(buf):
    """Calculate the checksum for a member's header by summing up all
       characters except for the chksum field which is treated as if
       it was filled with spaces. According to the GNU tar sources,
       some tars (Sun and NeXT) calculate chksum with signed char,
       which will be different if there are chars in the buffer with
       the high bit set. So we calculate two checksums, unsigned and
       signed.
    """
    unsigned_chksum = 256 + sum(struct.unpack("148B", buf[:148]) + struct.unpack("356B", buf[156:512]))
    signed_chksum = 256 + sum(struct.unpack("148b", buf[:148]) + struct.unpack("356b", buf[156:512]))
    return unsigned_chksum, signed_chksum

class TarError(Exception):
    """Base exception."""
    pass
class ExtractError(TarError):
    """General exception for extract errors."""
    pass
class ReadError(TarError):
    """Exception for unreadable tar archives."""
    pass
class CompressionError(TarError):
    """Exception for unavailable compression methods."""
    pass
class StreamError(TarError):
    """Exception for unsupported operations on stream-like TarFile2s."""
    pass
class HeaderError(TarError):
    """Base exception for header errors."""
    pass
class EmptyHeaderError(HeaderError):
    """Exception for empty headers."""
    pass
class TruncatedHeaderError(HeaderError):
    """Exception for truncated headers."""
    pass
class EOFHeaderError(HeaderError):
    """Exception for end of file headers."""
    pass
class InvalidHeaderError(HeaderError):
    """Exception for invalid headers."""
    pass
class SubsequentHeaderError(HeaderError):
    """Exception for missing and invalid extended headers."""
    pass

#------------------------
# Extraction file object
#------------------------
class _FileInFile2(object):
    """A thin wrapper around an existing file object that
       provides a part of its data as an individual file
       object.
    """

    def __init__(self, fileobj, offset, size, sparse=None):
        self.fileobj = fileobj
        self.offset = offset
        self.size = size
        self.sparse = sparse
        self.position = 0

    def tell(self):
        """Return the current file position.
        """
        return self.position

    def seek(self, position):
        """Seek to a position in the file.
        """
        self.position = position

    def read(self, size=None):
        """Read data from the file.
        """
        if size is None:
            size = self.size - self.position
        else:
            size = min(size, self.size - self.position)

        if self.sparse is None:
            return self.readnormal(size)
        else:
            return self.readsparse(size)

    def __read(self, size):
        buf = self.fileobj.read(size)
        if len(buf) != size:
            raise ReadError("unexpected end of data")
        return buf

    def readnormal(self, size):
        """Read operation for regular files.
        """
        self.fileobj.seek(self.offset + self.position)
        self.position += size
        return self.__read(size)
#class _FileInFile2

class ExFileObject2(object):
    """File-like object for reading an archive member.
       Is returned by TarFile2.extractfile().
    """
    blocksize = 1024

    def __init__(self, tarfile, tarinfo):
        self.fileobj = _FileInFile2(tarfile.fileobj,
                                   tarinfo.offset_data,
                                   tarinfo.size,
                                   getattr(tarinfo, "sparse", None))
        self.name = tarinfo.name
        self.mode = "r"
        self.closed = False
        self.size = tarinfo.size

        self.position = 0
        self.buffer = ""

    def read(self, size=None):
        """Read at most size bytes from the file. If size is not
           present or None, read all data until EOF is reached.
        """
        if self.closed:
            raise ValueError("I/O operation on closed file")

        buf = ""
        if self.buffer:
            if size is None:
                buf = self.buffer
                self.buffer = ""
            else:
                buf = self.buffer[:size]
                self.buffer = self.buffer[size:]

        if size is None:
            buf += self.fileobj.read()
        else:
            buf += self.fileobj.read(size - len(buf))

        self.position += len(buf)
        return buf

    def tell(self):
        """Return the current file position.
        """
        if self.closed:
            raise ValueError("I/O operation on closed file")

        return self.position

    def seek(self, pos, whence=os.SEEK_SET):
        """Seek to a position in the file.
        """
        if self.closed:
            raise ValueError("I/O operation on closed file")

        if whence == os.SEEK_SET:
            self.position = min(max(pos, 0), self.size)
        elif whence == os.SEEK_CUR:
            if pos < 0:
                self.position = max(self.position + pos, 0)
            else:
                self.position = min(self.position + pos, self.size)
        elif whence == os.SEEK_END:
            self.position = max(min(self.size + pos, self.size), 0)
        else:
            raise ValueError("Invalid argument")

        self.buffer = ""
        self.fileobj.seek(self.position)

    def close(self):
        """Close the file object.
        """
        self.closed = True

    def __iter__(self):
        """Get an iterator over the file's lines.
        """
        while True:
            line = self.readline()
            if not line:
                break
            yield line
#class ExFileObject2

#------------------
# Exported Classes
#------------------
class TarInfo2(object):
    """Informational class which holds the details about an
       archive member given by a tar header block.
       TarInfo2 objects are returned by TarFile2.getmember(),
       TarFile2.getmembers() and TarFile2.gettarinfo() and are
       usually created internally.
    """

    def __init__(self, name=""):
        """Construct a TarInfo2 object. name is the optional name
           of the member.
        """
        self.name = name        # member name
        self.mode = 0o644        # file permissions
        self.uid = 0            # user id
        self.gid = 0            # group id
        self.size = 0           # file size
        self.mtime = 0          # modification time
        self.chksum = 0         # header checksum
        self.type = REGTYPE     # member type
        self.linkname = ""      # link name
        self.uname = ""         # user name
        self.gname = ""         # group name
        self.devmajor = 0       # device major number
        self.devminor = 0       # device minor number

        self.offset = 0         # the tar header starts here
        self.offset_data = 0    # the file's data starts here

        self.pax_headers = {}   # pax header information

    # In pax headers the "name" and "linkname" field are called
    # "path" and "linkpath".
    def _getpath(self):
        return self.name
    def _setpath(self, name):
        self.name = name
    path = property(_getpath, _setpath)

    def _getlinkpath(self):
        return self.linkname
    def _setlinkpath(self, linkname):
        self.linkname = linkname
    linkpath = property(_getlinkpath, _setlinkpath)

    def __repr__(self):
        return "<%s %r at %#x>" % (self.__class__.__name__,self.name,id(self))

    @classmethod
    def frombuf(cls, buf):
        """Construct a TarInfo2 object from a 512 byte string buffer.
        """
        if len(buf) == 0:
            raise EmptyHeaderError("empty header")
        if len(buf) != BLOCKSIZE:
            raise TruncatedHeaderError("truncated header")
        if buf.count(NUL) == BLOCKSIZE:
            raise EOFHeaderError("end of file header")

        chksum = nti(buf[148:156])
        if chksum not in calc_chksums(buf):
            raise InvalidHeaderError("bad checksum")

        obj = cls()
        obj.buf = buf
        obj.name = nts(buf[0:100])
        obj.mode = nti(buf[100:108])
        obj.uid = nti(buf[108:116])
        obj.gid = nti(buf[116:124])
        obj.size = nti(buf[124:136])
        obj.mtime = nti(buf[136:148])
        obj.chksum = chksum
        obj.type = buf[156:157]
        obj.linkname = nts(buf[157:257])
        obj.uname = nts(buf[265:297])
        obj.gname = nts(buf[297:329])
        obj.devmajor = nti(buf[329:337])
        obj.devminor = nti(buf[337:345])
        prefix = nts(buf[345:500])

        # Old V7 tar format represents a directory as a regular
        # file with a trailing slash.
        if obj.type == AREGTYPE and obj.name.endswith("/"):
            obj.type = DIRTYPE

        # Remove redundant slashes from directories.
        if obj.isdir():
            obj.name = obj.name.rstrip("/")

        # Reconstruct a ustar longname.
        if prefix and obj.type not in GNU_TYPES:
            obj.name = prefix + "/" + obj.name
        return obj

    @classmethod
    def fromtarfile(cls, tarfile):
        """Return the next TarInfo2 object from TarFile2 object
           tarfile.
        """
        buf = tarfile.fileobj.read(BLOCKSIZE)
        obj = cls.frombuf(buf)
        obj.offset = tarfile.fileobj.tell() - BLOCKSIZE
        return obj._proc_member(tarfile)

    def _proc_member(self, tarfile):
        """Choose the right processing method depending on
           the type and call it.
        """
        if self.type in (GNUTYPE_LONGNAME, GNUTYPE_LONGLINK):
            return self._proc_gnulong(tarfile)
        elif self.type == GNUTYPE_SPARSE:
            return self._proc_sparse(tarfile)
        elif self.type in (XHDTYPE, XGLTYPE, SOLARIS_XHDTYPE):
            return self._proc_pax(tarfile)
        else:
            return self._proc_builtin(tarfile)

    def _proc_builtin(self, tarfile):
        """Process a builtin type or an unknown type which
           will be treated as a regular file.
        """
        self.offset_data = tarfile.fileobj.tell()
        offset = self.offset_data
        if self.isreg() or self.type not in SUPPORTED_TYPES:
            # Skip the following data blocks.
            offset += self._block(self.size)
        tarfile.offset = offset

        # Patch the TarInfo2 object with saved global
        # header information.
        self._apply_pax_info(tarfile.pax_headers, tarfile.encoding, tarfile.errors)

        return self

    def _apply_pax_info(self, pax_headers, encoding, errors):
        """Replace fields with supplemental information from a previous
           pax extended or global header.
        """
        for keyword, value in pax_headers.iteritems():
            if keyword not in PAX_FIELDS:
                continue

            if keyword == "path":
                value = value.rstrip("/")

            if keyword in PAX_NUMBER_FIELDS:
                try:
                    value = PAX_NUMBER_FIELDS[keyword](value)
                except ValueError:
                    value = 0
            else:
                value = uts(value, encoding, errors)

            setattr(self, keyword, value)

        self.pax_headers = pax_headers.copy()

    def _block(self, count):
        """Round up a byte count by BLOCKSIZE and return it,
           e.g. _block(834) => 1024.
        """
        blocks, remainder = divmod(count, BLOCKSIZE)
        if remainder:
            blocks += 1
        return blocks * BLOCKSIZE

    def isreg(self):
        return self.type in REGULAR_TYPES
    def isfile(self):
        return self.isreg()
    def isdir(self):
        return self.type == DIRTYPE
    def issym(self):
        return self.type == SYMTYPE
    def islnk(self):
        return self.type == LNKTYPE
    def ischr(self):
        return self.type == CHRTYPE
    def isblk(self):
        return self.type == BLKTYPE
    def isfifo(self):
        return self.type == FIFOTYPE
    def issparse(self):
        return self.type == GNUTYPE_SPARSE
    def isdev(self):
        return self.type in (CHRTYPE, BLKTYPE, FIFOTYPE)
# class TarInfo2

class TarFile2(object):
    """The TarFile2 Class provides an interface to tar archives.
    """

    debug = 0                   # May be set from 0 (no msgs) to 3 (all msgs)

    dereference = False         # If true, add content of linked file to the
                                # tar file, else the link.

    ignore_zeros = False        # If true, skips empty or invalid blocks and
                                # continues processing.

    errorlevel = 1              # If 0, fatal errors only appear in debug
                                # messages (if debug >= 0). If > 0, errors
                                # are passed to the caller as exceptions.

    format = DEFAULT_FORMAT     # The format to use when creating an archive.

    encoding = ENCODING         # Encoding for 8-bit character strings.

    errors = None               # Error handler for unicode conversion.

    tarinfo = TarInfo2           # The default TarInfo2 class to use.

    fileobject = ExFileObject2   # The default ExFileObject2 class to use.

    def __init__(self, name=None, mode="r", fileobj=None, format=None,
            tarinfo=None, dereference=None, ignore_zeros=None, encoding=None,
            errors=None, pax_headers=None, debug=None, errorlevel=None):
        """Open an (uncompressed) tar archive `name'. `mode' is either 'r' to
           read from an existing archive, 'a' to append data to an existing
           file or 'w' to create a new file overwriting an existing one. `mode'
           defaults to 'r'.
           If `fileobj' is given, it is used for reading or writing data. If it
           can be determined, `mode' is overridden by `fileobj's mode.
           `fileobj' is not closed, when TarFile2 is closed.
        """
        modes = {"r": "rb", "a": "r+b", "w": "wb"}
        if mode not in modes:
            raise ValueError("mode must be 'r', 'a' or 'w'")
        self.mode = mode
        self._mode = modes[mode]

        if not fileobj:
            if self.mode == "a" and not os.path.exists(name):
                # Create nonexistent files in append mode.
                self.mode = "w"
                self._mode = "wb"
            fileobj = bltn_open(name, self._mode)
            self._extfileobj = False
        else:
            if name is None and hasattr(fileobj, "name"):
                name = fileobj.name
            if hasattr(fileobj, "mode"):
                self._mode = fileobj.mode
            self._extfileobj = True
        self.name = os.path.abspath(name) if name else None
        self.fileobj = fileobj

        # Init attributes.
        if format is not None:
            self.format = format
        if tarinfo is not None:
            self.tarinfo = tarinfo
        if dereference is not None:
            self.dereference = dereference
        if ignore_zeros is not None:
            self.ignore_zeros = ignore_zeros
        if encoding is not None:
            self.encoding = encoding

        if errors is not None:
            self.errors = errors
        elif mode == "r":
            self.errors = "utf-8"
        else:
            self.errors = "strict"

        if pax_headers is not None and self.format == PAX_FORMAT:
            self.pax_headers = pax_headers
        else:
            self.pax_headers = {}

        if debug is not None:
            self.debug = debug
        if errorlevel is not None:
            self.errorlevel = errorlevel

        # Init datastructures.
        self.closed = False
        self.members = []       # list of members as TarInfo2 objects
        self._loaded = False    # flag if all members have been read
        self.offset = self.fileobj.tell()
                                # current position in the archive file
        self.inodes = {}        # dictionary caching the inodes of
                                # archive members already added

        try:
            if self.mode == "r":
                self.firstmember = None
                self.firstmember = self.next()

            if self.mode == "a":
                # Move to the end of the archive,
                # before the first empty block.
                while True:
                    self.fileobj.seek(self.offset)
                    try:
                        tarinfo = self.tarinfo.fromtarfile(self)
                        self.members.append(tarinfo)
                    except EOFHeaderError:
                        self.fileobj.seek(self.offset)
                        break
                    except HeaderError as e:
                        raise ReadError(str(e))

            if self.mode in "aw":
                self._loaded = True

                if self.pax_headers:
                    buf = self.tarinfo.create_pax_global_header(self.pax_headers.copy())
                    self.fileobj.write(buf)
                    self.offset += len(buf)
        except:
            if not self._extfileobj:
                self.fileobj.close()
            self.closed = True
            raise

    @classmethod
    def open(cls, name=None, mode="r", fileobj=None, bufsize=RECORDSIZE, **kwargs):
        """Open a tar archive for reading, writing or appending. Return
           an appropriate TarFile2 class.

           mode:
           'r' or 'r:*' open for reading with transparent compression
           'r:'         open for reading exclusively uncompressed
           'r:gz'       open for reading with gzip compression
           'r:bz2'      open for reading with bzip2 compression
           'a' or 'a:'  open for appending, creating the file if necessary
           'w' or 'w:'  open for writing without compression
           'w:gz'       open for writing with gzip compression
           'w:bz2'      open for writing with bzip2 compression

           'r|*'        open a stream of tar blocks with transparent compression
           'r|'         open an uncompressed stream of tar blocks for reading
           'r|gz'       open a gzip compressed stream of tar blocks
           'r|bz2'      open a bzip2 compressed stream of tar blocks
           'w|'         open an uncompressed stream for writing
           'w|gz'       open a gzip compressed stream for writing
           'w|bz2'      open a bzip2 compressed stream for writing
        """

        if not name and not fileobj:
            raise ValueError("nothing to open")

        if mode in ("r", "r:*"):
            # Find out which *open() is appropriate for opening the file.
            def not_compressed(comptype):
                return cls.OPEN_METH[comptype] == 'taropen'
            for comptype in sorted(cls.OPEN_METH, key=not_compressed):
                func = getattr(cls, cls.OPEN_METH[comptype])
                if fileobj is not None:
                    saved_pos = fileobj.tell()
                try:
                    return func(name, "r", fileobj, **kwargs)
                except (ReadError, CompressionError) as e:
                    if fileobj is not None:
                        fileobj.seek(saved_pos)
                    continue
            raise ReadError("file could not be opened successfully")

        elif ":" in mode:
            filemode, comptype = mode.split(":", 1)
            filemode = filemode or "r"
            comptype = comptype or "tar"

            # Select the *open() function according to
            # given compression.
            if comptype in cls.OPEN_METH:
                func = getattr(cls, cls.OPEN_METH[comptype])
            else:
                raise CompressionError("unknown compression type %r" % comptype)
            return func(name, filemode, fileobj, **kwargs)

        elif mode in ("a", "w"):
            return cls.taropen(name, mode, fileobj, **kwargs)

        raise ValueError("undiscernible mode")

    @classmethod
    def taropen(cls, name, mode="r", fileobj=None, **kwargs):
        """Open uncompressed tar archive name for reading or writing.
        """
        if mode not in ("r", "a", "w"):
            raise ValueError("mode must be 'r', 'a' or 'w'")
        return cls(name, mode, fileobj, **kwargs)

    @classmethod
    def gzopen(cls, name, mode="r", fileobj=None, compresslevel=9, **kwargs):
        """Open gzip compressed tar archive name for reading or writing.
           Appending is not allowed.
        """
        if mode not in ("r", "w"):
            raise ValueError("mode must be 'r' or 'w'")

        try:
            import gzip
            gzip.GzipFile
        except (ImportError, AttributeError):
            raise CompressionError("gzip module is not available")

        try:
            fileobj = gzip.GzipFile(name, mode, compresslevel, fileobj)
        except OSError:
            if fileobj is not None and mode == 'r':
                raise ReadError("not a gzip file")
            raise

        try:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        except IOError:
            fileobj.close()
            if mode == 'r':
                raise ReadError("not a gzip file")
            raise
        except:
            fileobj.close()
            raise
        t._extfileobj = False
        return t

    @classmethod
    def bz2open(cls, name, mode="r", fileobj=None, compresslevel=9, **kwargs):
        """Open bzip2 compressed tar archive name for reading or writing.
           Appending is not allowed.
        """
        if mode not in ("r", "w"):
            raise ValueError("mode must be 'r' or 'w'.")

        try:
            import bz2
        except ImportError:
            raise CompressionError("bz2 module is not available")

        if fileobj is not None:
            fileobj = _BZ2Proxy2(fileobj, mode)
        else:
            fileobj = bz2.BZ2File(name, mode, compresslevel=compresslevel)

        try:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        except (IOError, EOFError):
            fileobj.close()
            if mode == 'r':
                raise ReadError("not a bzip2 file")
            raise
        except:
            fileobj.close()
            raise
        t._extfileobj = False
        return t

    # All *open() methods are registered here.
    OPEN_METH = {
        "tar": "taropen",   # uncompressed tar
        "gz":  "gzopen",    # gzip compressed tar
        "bz2": "bz2open"    # bzip2 compressed tar
    }

    #--------------------------------------------------------------------------
    # The public methods which TarFile2 provides:

    def close(self):
        """Close the TarFile2. In write-mode, two finishing zero blocks are
           appended to the archive.
        """
        if self.closed:
            return

        self.closed = True
        try:
            if self.mode in "aw":
                self.fileobj.write(NUL * (BLOCKSIZE * 2))
                self.offset += (BLOCKSIZE * 2)
                # fill up the end with zero-blocks
                # (like option -b20 for tar does)
                blocks, remainder = divmod(self.offset, RECORDSIZE)
                if remainder > 0:
                    self.fileobj.write(NUL * (RECORDSIZE - remainder))
        finally:
            if not self._extfileobj:
                self.fileobj.close()

    def getmember(self, name):
        """Return a TarInfo2 object for member `name'. If `name' can not be
           found in the archive, KeyError is raised. If a member occurs more
           than once in the archive, its last occurrence is assumed to be the
           most up-to-date version.
        """
        tarinfo = self._getmember(name)
        if tarinfo is None:
            raise KeyError("filename %r not found" % name)
        return tarinfo

    def getmembers(self):
        """Return the members of the archive as a list of TarInfo2 objects. The
           list has the same order as the members in the archive.
        """
        self._check()
        if not self._loaded:    # if we want to obtain a list of
            self._load()        # all members, we first have to
                                # scan the whole archive.
        return self.members

    def extractfile(self, member):
        """Extract a member from the archive as a file object. `member' may be
           a filename or a TarInfo2 object. If `member' is a regular file, a
           file-like object is returned. If `member' is a link, a file-like
           object is constructed from the link's target. If `member' is none of
           the above, None is returned.
           The file-like object is read-only and provides the following
           methods: read(), readline(), readlines(), seek() and tell()
        """
        self._check("r")

        if isinstance(member, basestring):
            tarinfo = self.getmember(member)
        else:
            tarinfo = member

        if tarinfo.isreg():
            return self.fileobject(self, tarinfo)

        elif tarinfo.type not in SUPPORTED_TYPES:
            # If a member's type is unknown, it is treated as a
            # regular file.
            return self.fileobject(self, tarinfo)

        elif tarinfo.islnk() or tarinfo.issym():
            if isinstance(self.fileobj, _Stream2):
                # A small but ugly workaround for the case that someone tries
                # to extract a (sym)link as a file-object from a non-seekable
                # stream of tar blocks.
                raise StreamError("cannot extract (sym)link as file object")
            else:
                # A (sym)link's file object is its target's file object.
                return self.extractfile(self._find_link_target(tarinfo))
        else:
            # If there's no data associated with the member (directory, chrdev,
            # blkdev, etc.), return None instead of a file object.
            return None

    #--------------------------------------------------------------------------
    def next(self):
        """Return the next member of the archive as a TarInfo2 object, when
           TarFile2 is opened for reading. Return None if there is no more
           available.
        """
        self._check("ra")
        if self.firstmember is not None:
            m = self.firstmember
            self.firstmember = None
            return m

        # Advance the file pointer.
        if self.offset != self.fileobj.tell():
            self.fileobj.seek(self.offset - 1)
            if not self.fileobj.read(1):
                raise ReadError("unexpected end of data")

        # Read the next block.
        tarinfo = None
        while True:
            try:
                tarinfo = self.tarinfo.fromtarfile(self)
            except EOFHeaderError as e:
                if self.ignore_zeros:
                    self._dbg(2, "0x%X: %s" % (self.offset, e))
                    self.offset += BLOCKSIZE
                    continue
            except InvalidHeaderError as e:
                if self.ignore_zeros:
                    self._dbg(2, "0x%X: %s" % (self.offset, e))
                    self.offset += BLOCKSIZE
                    continue
                elif self.offset == 0:
                    raise ReadError(str(e))
            except EmptyHeaderError:
                if self.offset == 0:
                    raise ReadError("empty file")
            except TruncatedHeaderError as e:
                if self.offset == 0:
                    raise ReadError(str(e))
            except SubsequentHeaderError as e:
                raise ReadError(str(e))
            break

        if tarinfo is not None:
            self.members.append(tarinfo)
        else:
            self._loaded = True

        return tarinfo

    #--------------------------------------------------------------------------
    # Little helper methods:

    def _getmember(self, name, tarinfo=None, normalize=False):
        """Find an archive member by name from bottom to top.
           If tarinfo is given, it is used as the starting point.
        """
        # Ensure that all members have been loaded.
        members = self.getmembers()

        # Limit the member search list up to tarinfo.
        if tarinfo is not None:
            members = members[:members.index(tarinfo)]

        if normalize:
            name = os.path.normpath(name)

        for member in reversed(members):
            if normalize:
                member_name = os.path.normpath(member.name)
            else:
                member_name = member.name

            if name == member_name:
                return member

    def _load(self):
        """Read through the entire archive file and look for readable
           members.
        """
        while True:
            tarinfo = self.next()
            if tarinfo is None:
                break
        self._loaded = True

    def _check(self, mode=None):
        """Check if TarFile2 is still open, and if the operation's mode
           corresponds to TarFile2's mode.
        """
        if self.closed:
            raise IOError("%s is closed" % self.__class__.__name__)
        if mode is not None and self.mode not in mode:
            raise IOError("bad operation for mode %r" % self.mode)

    def _find_link_target(self, tarinfo):
        """Find the target member of a symlink or hardlink member in the
           archive.
        """
        if tarinfo.issym():
            # Always search the entire archive.
            linkname = "/".join(filter(None, (os.path.dirname(tarinfo.name), tarinfo.linkname)))
            limit = None
        else:
            # Search the archive before the link, because a hard link is
            # just a reference to an already archived file.
            linkname = tarinfo.linkname
            limit = tarinfo

        member = self._getmember(linkname, tarinfo=limit, normalize=True)
        if member is None:
            raise KeyError("linkname %r not found" % linkname)
        return member

    def __iter__(self):
        """Provide an iterator object.
        """
        if self._loaded:
            return iter(self.members)
        else:
            return TarIter2(self)

    def _dbg(self, level, msg):
        """Write debugging output to sys.stderr.
        """
        if level <= self.debug:
            print >> sys.stderr, msg

    def __enter__(self):
        self._check()
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            self.close()
        else:
            # An exception occurred. We must not call close() because
            # it would try to write end-of-archive blocks and padding.
            if not self._extfileobj:
                self.fileobj.close()
            self.closed = True
# class TarFile2

#-------------------------------------------------------------------------------


################################################################################
#                                                                              #
# This is only a PART of TARFILE LIBRARY - needed to CHECK TAR file INTEGRITY. #
# It contains PATCH TO BUG present in python 2.6, 2.7, 3.4, 3.5.               #
#                                                                              #
# The bug allowed to extract corrupted tar file without raising any errors     #
# (regardless of errorlevel setting).                                          #
#                                                                              #
# There are two versions used by this script - for python 2.* and 3.0-3.5.     #
# Below you can find version used by this script for python [ 3.0-3.5 ].       #
#                                                                              #
# link to discussion:       https://bugs.python.org/issue24259                 #
# link to patch:            https://hg.python.org/cpython/rev/c7f4f61697b7     #
#                                                                              #
# date:         17 Jan 2017                                                    #
# link:         https://hg.python.org/cpython/file/3.4/Lib/tarfile.py          #
#                                                                              #
################################################################################

#-------------------------------------------------------------------
# tarfile.py   [[[   branch 3.4   ]]] - used in this script for python 3.0-3.5
#-------------------------------------------------------------------
# Copyright (C) 2002 Lars Gustaebel <lars@gustaebel.de>
# All rights reserved.
#
# Permission  is  hereby granted,  free  of charge,  to  any person
# obtaining a  copy of  this software  and associated documentation
# files  (the  "Software"),  to   deal  in  the  Software   without
# restriction,  including  without limitation  the  rights to  use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies  of  the  Software,  and to  permit  persons  to  whom the
# Software  is  furnished  to  do  so,  subject  to  the  following
# conditions:
#
# The above copyright  notice and this  permission notice shall  be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS  IS", WITHOUT WARRANTY OF ANY  KIND,
# EXPRESS OR IMPLIED, INCLUDING  BUT NOT LIMITED TO  THE WARRANTIES
# OF  MERCHANTABILITY,  FITNESS   FOR  A  PARTICULAR   PURPOSE  AND
# NONINFRINGEMENT.  IN  NO  EVENT SHALL  THE  AUTHORS  OR COPYRIGHT
# HOLDERS  BE LIABLE  FOR ANY  CLAIM, DAMAGES  OR OTHER  LIABILITY,
# WHETHER  IN AN  ACTION OF  CONTRACT, TORT  OR OTHERWISE,  ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#

#---------------------------------------------------------
# Some useful functions
#---------------------------------------------------------
def stn3(s, length, encoding, errors):
    """Convert a string to a null-terminated bytes object.
    """
    s = s.encode(encoding, errors)
    return s[:length] + (length - len(s)) * NUL

def nts3(s, encoding, errors):
    """Convert a null-terminated bytes object to a string.
    """
    p = s.find(b"\0")
    if p != -1:
        s = s[:p]
    return s.decode(encoding, errors)

def nti3(s):
    """Convert a number field to a python number.
    """
    # There are two possible encodings for a number field, see
    # itn3() below.
    if s[0] in (0o200, 0o377):
        n = 0
        for i in range(len(s) - 1):
            n <<= 8
            n += s[i + 1]
        if s[0] == 0o377:
            n = -(256 ** (len(s) - 1) - n)
    else:
        try:
            s = nts3(s, "ascii", "strict")
            n = int(s.strip() or "0", 8)
        except ValueError:
            raise InvalidHeaderError("invalid header")
    return n

def itn3(n, digits=8, format=DEFAULT_FORMAT):
    """Convert a python number to a number field.
    """
    # POSIX 1003.1-1988 requires numbers to be encoded as a string of
    # octal digits followed by a null-byte, this allows values up to
    # (8**(digits-1))-1. GNU tar allows storing numbers greater than
    # that if necessary. A leading 0o200 or 0o377 byte indicate this
    # particular encoding, the following digits-1 bytes are a big-endian
    # base-256 representation. This allows values up to (256**(digits-1))-1.
    # A 0o200 byte indicates a positive number, a 0o377 byte a negative
    # number.
    if 0 <= n < 8 ** (digits - 1):
        s = bytes("%0*o" % (digits - 1, int(n)), "ascii") + NUL
    elif format == GNU_FORMAT and -256 ** (digits - 1) <= n < 256 ** (digits - 1):
        if n >= 0:
            s = bytearray([0o200])
        else:
            s = bytearray([0o377])
            n = 256 ** digits + n

        for i in range(digits - 1):
            s.insert(1, n & 0o377)
            n >>= 8
    else:
        raise ValueError("overflow in number field")

    return s

def calc_chksums3(buf):
    """Calculate the checksum for a member's header by summing up all
       characters except for the chksum field which is treated as if
       it was filled with spaces. According to the GNU tar sources,
       some tars (Sun and NeXT) calculate chksum with signed char,
       which will be different if there are chars in the buffer with
       the high bit set. So we calculate two checksums, unsigned and
       signed.
    """
    unsigned_chksum = 256 + sum(struct.unpack_from("148B8x356B", buf))
    signed_chksum = 256 + sum(struct.unpack_from("148b8x356b", buf))
    return unsigned_chksum, signed_chksum

#------------------------
# Extraction file object
#------------------------
class _FileInFile3(object):
    """A thin wrapper around an existing file object that
       provides a part of its data as an individual file
       object.
    """

    def __init__(self, fileobj, offset, size, blockinfo=None):
        self.fileobj = fileobj
        self.offset = offset
        self.size = size
        self.position = 0
        self.name = getattr(fileobj, "name", None)
        self.closed = False

        if blockinfo is None:
            blockinfo = [(0, size)]

        # Construct a map with data and zero blocks.
        self.map_index = 0
        self.map = []
        lastpos = 0
        realpos = self.offset
        for offset, size in blockinfo:
            if offset > lastpos:
                self.map.append((False, lastpos, offset, None))
            self.map.append((True, offset, offset + size, realpos))
            realpos += size
            lastpos = offset + size
        if lastpos < self.size:
            self.map.append((False, lastpos, self.size, None))

    def flush(self):
        pass

    def readable(self):
        return True

    def writable(self):
        return False

    def seekable(self):
        return self.fileobj.seekable()

    def tell(self):
        """Return the current file position.
        """
        return self.position

    #def seek(self, position, whence=io.SEEK_SET):
    def seek(self, position, whence=os.SEEK_SET):
    #def seek(self, position, whence=0):
        # SEEK_SET or 0 - start of the stream (the default); offset should be zero or positive
        # SEEK_CUR or 1 - current stream position; offset may be negative
        # SEEK_END or 2 - end of the stream; offset is usually negative
        """Seek to a position in the file.
        """
        if whence == io.SEEK_SET:
            self.position = min(max(position, 0), self.size)
        elif whence == io.SEEK_CUR:
            if position < 0:
                self.position = max(self.position + position, 0)
            else:
                self.position = min(self.position + position, self.size)
        elif whence == io.SEEK_END:
            self.position = max(min(self.size + position, self.size), 0)
        else:
            raise ValueError("Invalid argument")
        return self.position

    def read(self, size=None):
        """Read data from the file.
        """
        if size is None:
            size = self.size - self.position
        else:
            size = min(size, self.size - self.position)

        buf = b""
        while size > 0:
            while True:
                data, start, stop, offset = self.map[self.map_index]
                if start <= self.position < stop:
                    break
                else:
                    self.map_index += 1
                    if self.map_index == len(self.map):
                        self.map_index = 0
            length = min(size, stop - self.position)
            if data:
                self.fileobj.seek(offset + (self.position - start))
                b = self.fileobj.read(length)
                if len(b) != length:
                    raise ReadError("unexpected end of data")
                buf += b
            else:
                buf += NUL * length
            size -= length
            self.position += length
        return buf

    def readinto(self, b):
        buf = self.read(len(b))
        b[:len(buf)] = buf
        return len(buf)

    def close(self):
        self.closed = True
#class _FileInFile3

class ExFileObject3(io.BufferedReader):

    def __init__(self, tarfile, tarinfo):
        fileobj = _FileInFile3(tarfile.fileobj, tarinfo.offset_data,
                tarinfo.size, tarinfo.sparse)
        super().__init__(fileobj)
#class ExFileObject3

#------------------
# Exported Classes
#------------------
class TarInfo3(object):
    """Informational class which holds the details about an
       archive member given by a tar header block.
       TarInfo3 objects are returned by TarFile3.getmember(),
       TarFile3.getmembers() and TarFile3.gettarinfo() and are
       usually created internally.
    """

    __slots__ = ("name", "mode", "uid", "gid", "size", "mtime",
                 "chksum", "type", "linkname", "uname", "gname",
                 "devmajor", "devminor",
                 "offset", "offset_data", "pax_headers", "sparse",
                 "tarfile", "_sparse_structs", "_link_target")

    def __init__(self, name=""):
        """Construct a TarInfo3 object. name is the optional name
           of the member.
        """
        self.name = name        # member name
        self.mode = 0o644       # file permissions
        self.uid = 0            # user id
        self.gid = 0            # group id
        self.size = 0           # file size
        self.mtime = 0          # modification time
        self.chksum = 0         # header checksum
        self.type = REGTYPE     # member type
        self.linkname = ""      # link name
        self.uname = ""         # user name
        self.gname = ""         # group name
        self.devmajor = 0       # device major number
        self.devminor = 0       # device minor number

        self.offset = 0         # the tar header starts here
        self.offset_data = 0    # the file's data starts here

        self.sparse = None      # sparse member information
        self.pax_headers = {}   # pax header information

    # In pax headers the "name" and "linkname" field are called
    # "path" and "linkpath".
    def _getpath(self):
        return self.name
    def _setpath(self, name):
        self.name = name
    path = property(_getpath, _setpath)

    def _getlinkpath(self):
        return self.linkname
    def _setlinkpath(self, linkname):
        self.linkname = linkname
    linkpath = property(_getlinkpath, _setlinkpath)

    def __repr__(self):
        return "<%s %r at %#x>" % (self.__class__.__name__,self.name,id(self))

    @classmethod
    def frombuf(cls, buf, encoding, errors):
        """Construct a TarInfo3 object from a 512 byte bytes object.
        """
        if len(buf) == 0:
            raise EmptyHeaderError("empty header")
        if len(buf) != BLOCKSIZE:
            raise TruncatedHeaderError("truncated header")
        if buf.count(NUL) == BLOCKSIZE:
            raise EOFHeaderError("end of file header")

        chksum = nti3(buf[148:156])
        if chksum not in calc_chksums3(buf):
            raise InvalidHeaderError("bad checksum")

        obj = cls()
        obj.name = nts3(buf[0:100], encoding, errors)
        obj.mode = nti3(buf[100:108])
        obj.uid = nti3(buf[108:116])
        obj.gid = nti3(buf[116:124])
        obj.size = nti3(buf[124:136])
        obj.mtime = nti3(buf[136:148])
        obj.chksum = chksum
        obj.type = buf[156:157]
        obj.linkname = nts3(buf[157:257], encoding, errors)
        obj.uname = nts3(buf[265:297], encoding, errors)
        obj.gname = nts3(buf[297:329], encoding, errors)
        obj.devmajor = nti3(buf[329:337])
        obj.devminor = nti3(buf[337:345])
        prefix = nts3(buf[345:500], encoding, errors)

        # Old V7 tar format represents a directory as a regular
        # file with a trailing slash.
        if obj.type == AREGTYPE and obj.name.endswith("/"):
            obj.type = DIRTYPE

        # Remove redundant slashes from directories.
        if obj.isdir():
            obj.name = obj.name.rstrip("/")

        # Reconstruct a ustar longname.
        if prefix and obj.type not in GNU_TYPES:
            obj.name = prefix + "/" + obj.name
        return obj

    @classmethod
    def fromtarfile(cls, tarfile):
        """Return the next TarInfo3 object from TarFile3 object
           tarfile.
        """
        buf = tarfile.fileobj.read(BLOCKSIZE)
        obj = cls.frombuf(buf, tarfile.encoding, tarfile.errors)
        obj.offset = tarfile.fileobj.tell() - BLOCKSIZE
        return obj._proc_member(tarfile)

    def _proc_member(self, tarfile):
        """Choose the right processing method depending on
           the type and call it.
        """
        if self.type in (GNUTYPE_LONGNAME, GNUTYPE_LONGLINK):
            return self._proc_gnulong(tarfile)
        elif self.type == GNUTYPE_SPARSE:
            return self._proc_sparse(tarfile)
        elif self.type in (XHDTYPE, XGLTYPE, SOLARIS_XHDTYPE):
            return self._proc_pax(tarfile)
        else:
            return self._proc_builtin(tarfile)

    def _proc_builtin(self, tarfile):
        """Process a builtin type or an unknown type which
           will be treated as a regular file.
        """
        self.offset_data = tarfile.fileobj.tell()
        offset = self.offset_data
        if self.isreg() or self.type not in SUPPORTED_TYPES:
            # Skip the following data blocks.
            offset += self._block(self.size)
        tarfile.offset = offset

        # Patch the TarInfo3 object with saved global
        # header information.
        self._apply_pax_info(tarfile.pax_headers, tarfile.encoding, tarfile.errors)

        return self

    def _apply_pax_info(self, pax_headers, encoding, errors):
        """Replace fields with supplemental information from a previous
           pax extended or global header.
        """
        for keyword, value in pax_headers.items():
            if keyword == "GNU.sparse.name":
                setattr(self, "path", value)
            elif keyword == "GNU.sparse.size":
                setattr(self, "size", int(value))
            elif keyword == "GNU.sparse.realsize":
                setattr(self, "size", int(value))
            elif keyword in PAX_FIELDS:
                if keyword in PAX_NUMBER_FIELDS:
                    try:
                        value = PAX_NUMBER_FIELDS[keyword](value)
                    except ValueError:
                        value = 0
                if keyword == "path":
                    value = value.rstrip("/")
                setattr(self, keyword, value)

        self.pax_headers = pax_headers.copy()

    def _decode_pax_field(self, value, encoding, fallback_encoding, fallback_errors):
        """Decode a single field from a pax record.
        """
        try:
            return value.decode(encoding, "strict")
        except UnicodeDecodeError:
            return value.decode(fallback_encoding, fallback_errors)

    def _block(self, count):
        """Round up a byte count by BLOCKSIZE and return it,
           e.g. _block(834) => 1024.
        """
        blocks, remainder = divmod(count, BLOCKSIZE)
        if remainder:
            blocks += 1
        return blocks * BLOCKSIZE

    def isreg(self):
        return self.type in REGULAR_TYPES
    def isfile(self):
        return self.isreg()
    def isdir(self):
        return self.type == DIRTYPE
    def issym(self):
        return self.type == SYMTYPE
    def islnk(self):
        return self.type == LNKTYPE
    def ischr(self):
        return self.type == CHRTYPE
    def isblk(self):
        return self.type == BLKTYPE
    def isfifo(self):
        return self.type == FIFOTYPE
    def issparse(self):
        return self.sparse is not None
    def isdev(self):
        return self.type in (CHRTYPE, BLKTYPE, FIFOTYPE)
# class TarInfo3

class TarFile3(object):
    """The TarFile3 Class provides an interface to tar archives.
    """

    debug = 0                   # May be set from 0 (no msgs) to 3 (all msgs)

    dereference = False         # If true, add content of linked file to the
                                # tar file, else the link.

    ignore_zeros = False        # If true, skips empty or invalid blocks and
                                # continues processing.

    errorlevel = 1              # If 0, fatal errors only appear in debug
                                # messages (if debug >= 0). If > 0, errors
                                # are passed to the caller as exceptions.

    format = DEFAULT_FORMAT     # The format to use when creating an archive.

    encoding = ENCODING         # Encoding for 8-bit character strings.

    errors = None               # Error handler for unicode conversion.

    tarinfo = TarInfo3           # The default TarInfo3 class to use.

    fileobject = ExFileObject3   # The file-object for extractfile().

    def __init__(self, name=None, mode="r", fileobj=None, format=None,
            tarinfo=None, dereference=None, ignore_zeros=None, encoding=None,
            errors="surrogateescape", pax_headers=None, debug=None, errorlevel=None):
        """Open an (uncompressed) tar archive `name'. `mode' is either 'r' to
           read from an existing archive, 'a' to append data to an existing
           file or 'w' to create a new file overwriting an existing one. `mode'
           defaults to 'r'.
           If `fileobj' is given, it is used for reading or writing data. If it
           can be determined, `mode' is overridden by `fileobj's mode.
           `fileobj' is not closed, when TarFile3 is closed.
        """
        modes = {"r": "rb", "a": "r+b", "w": "wb"}
        if mode not in modes:
            raise ValueError("mode must be 'r', 'a' or 'w'")
        self.mode = mode
        self._mode = modes[mode]

        if not fileobj:
            if self.mode == "a" and not os.path.exists(name):
                # Create nonexistent files in append mode.
                self.mode = "w"
                self._mode = "wb"
            fileobj = bltn_open(name, self._mode)
            self._extfileobj = False
        else:
            if (name is None and hasattr(fileobj, "name") and
                isinstance(fileobj.name, (str, bytes))):
                name = fileobj.name
            if hasattr(fileobj, "mode"):
                self._mode = fileobj.mode
            self._extfileobj = True
        self.name = os.path.abspath(name) if name else None
        self.fileobj = fileobj

        # Init attributes.
        if format is not None:
            self.format = format
        if tarinfo is not None:
            self.tarinfo = tarinfo
        if dereference is not None:
            self.dereference = dereference
        if ignore_zeros is not None:
            self.ignore_zeros = ignore_zeros
        if encoding is not None:
            self.encoding = encoding
        self.errors = errors

        if pax_headers is not None and self.format == PAX_FORMAT:
            self.pax_headers = pax_headers
        else:
            self.pax_headers = {}

        if debug is not None:
            self.debug = debug
        if errorlevel is not None:
            self.errorlevel = errorlevel

        # Init datastructures.
        self.closed = False
        self.members = []       # list of members as TarInfo3 objects
        self._loaded = False    # flag if all members have been read
        self.offset = self.fileobj.tell()
                                # current position in the archive file
        self.inodes = {}        # dictionary caching the inodes of
                                # archive members already added

        try:
            if self.mode == "r":
                self.firstmember = None
                self.firstmember = self.next()

            if self.mode == "a":
                # Move to the end of the archive,
                # before the first empty block.
                while True:
                    self.fileobj.seek(self.offset)
                    try:
                        tarinfo = self.tarinfo.fromtarfile(self)
                        self.members.append(tarinfo)
                    except EOFHeaderError:
                        self.fileobj.seek(self.offset)
                        break
                    except HeaderError as e:
                        raise ReadError(str(e))

            if self.mode in "aw":
                self._loaded = True

                if self.pax_headers:
                    buf = self.tarinfo.create_pax_global_header(self.pax_headers.copy())
                    self.fileobj.write(buf)
                    self.offset += len(buf)
        except:
            if not self._extfileobj:
                self.fileobj.close()
            self.closed = True
            raise

    @classmethod
    def open(cls, name=None, mode="r", fileobj=None, bufsize=RECORDSIZE, **kwargs):
        """Open a tar archive for reading, writing or appending. Return
           an appropriate TarFile3 class.

           mode:
           'r' or 'r:*' open for reading with transparent compression
           'r:'         open for reading exclusively uncompressed
           'r:gz'       open for reading with gzip compression
           'r:bz2'      open for reading with bzip2 compression
           'r:xz'       open for reading with lzma compression
           'a' or 'a:'  open for appending, creating the file if necessary
           'w' or 'w:'  open for writing without compression
           'w:gz'       open for writing with gzip compression
           'w:bz2'      open for writing with bzip2 compression
           'w:xz'       open for writing with lzma compression

           'r|*'        open a stream of tar blocks with transparent compression
           'r|'         open an uncompressed stream of tar blocks for reading
           'r|gz'       open a gzip compressed stream of tar blocks
           'r|bz2'      open a bzip2 compressed stream of tar blocks
           'r|xz'       open an lzma compressed stream of tar blocks
           'w|'         open an uncompressed stream for writing
           'w|gz'       open a gzip compressed stream for writing
           'w|bz2'      open a bzip2 compressed stream for writing
           'w|xz'       open an lzma compressed stream for writing
        """

        if not name and not fileobj:
            raise ValueError("nothing to open")

        if mode in ("r", "r:*"):
            # Find out which *open() is appropriate for opening the file.
            for comptype in cls.OPEN_METH:
                func = getattr(cls, cls.OPEN_METH[comptype])
                if fileobj is not None:
                    saved_pos = fileobj.tell()
                try:
                    return func(name, "r", fileobj, **kwargs)
                except (ReadError, CompressionError) as e:
                    if fileobj is not None:
                        fileobj.seek(saved_pos)
                    continue
            raise ReadError("file could not be opened successfully")

        elif ":" in mode:
            filemode, comptype = mode.split(":", 1)
            filemode = filemode or "r"
            comptype = comptype or "tar"

            # Select the *open() function according to
            # given compression.
            if comptype in cls.OPEN_METH:
                func = getattr(cls, cls.OPEN_METH[comptype])
            else:
                raise CompressionError("unknown compression type %r" % comptype)
            return func(name, filemode, fileobj, **kwargs)

        elif mode in ("a", "w"):
            return cls.taropen(name, mode, fileobj, **kwargs)

        raise ValueError("undiscernible mode")

    @classmethod
    def taropen(cls, name, mode="r", fileobj=None, **kwargs):
        """Open uncompressed tar archive name for reading or writing.
        """
        if mode not in ("r", "a", "w"):
            raise ValueError("mode must be 'r', 'a' or 'w'")
        return cls(name, mode, fileobj, **kwargs)

    @classmethod
    def gzopen(cls, name, mode="r", fileobj=None, compresslevel=9, **kwargs):
        """Open gzip compressed tar archive name for reading or writing.
           Appending is not allowed.
        """
        if mode not in ("r", "w"):
            raise ValueError("mode must be 'r' or 'w'")

        try:
            import gzip
            gzip.GzipFile
        except (ImportError, AttributeError):
            raise CompressionError("gzip module is not available")

        try:
            fileobj = gzip.GzipFile(name, mode + "b", compresslevel, fileobj)
        except OSError:
            if fileobj is not None and mode == 'r':
                raise ReadError("not a gzip file")
            raise

        try:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        except OSError:
            fileobj.close()
            if mode == 'r':
                raise ReadError("not a gzip file")
            raise
        except:
            fileobj.close()
            raise
        t._extfileobj = False
        return t

    @classmethod
    def bz2open(cls, name, mode="r", fileobj=None, compresslevel=9, **kwargs):
        """Open bzip2 compressed tar archive name for reading or writing.
           Appending is not allowed.
        """
        if mode not in ("r", "w"):
            raise ValueError("mode must be 'r' or 'w'.")

        try:
            import bz2
        except ImportError:
            raise CompressionError("bz2 module is not available")

        fileobj = bz2.BZ2File(fileobj or name, mode,
                              compresslevel=compresslevel)

        try:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        except (OSError, EOFError):
            fileobj.close()
            if mode == 'r':
                raise ReadError("not a bzip2 file")
            raise
        except:
            fileobj.close()
            raise
        t._extfileobj = False
        return t

    @classmethod
    def xzopen(cls, name, mode="r", fileobj=None, preset=None, **kwargs):
        """Open lzma compressed tar archive name for reading or writing.
           Appending is not allowed.
        """
        if mode not in ("r", "w"):
            raise ValueError("mode must be 'r' or 'w'")

        try:
            import lzma
        except ImportError:
            raise CompressionError("lzma module is not available")

        fileobj = lzma.LZMAFile(fileobj or name, mode, preset=preset)

        try:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        except (lzma.LZMAError, EOFError):
            fileobj.close()
            if mode == 'r':
                raise ReadError("not an lzma file")
            raise
        except:
            fileobj.close()
            raise
        t._extfileobj = False
        return t

    # All *open() methods are registered here.
    OPEN_METH = {
        "tar": "taropen",   # uncompressed tar
        "gz":  "gzopen",    # gzip compressed tar
        "bz2": "bz2open",   # bzip2 compressed tar
        "xz":  "xzopen"     # lzma compressed tar
    }

    #--------------------------------------------------------------------------
    # The public methods which TarFile3 provides:

    def close(self):
        """Close the TarFile3. In write-mode, two finishing zero blocks are
           appended to the archive.
        """
        if self.closed:
            return

        self.closed = True
        try:
            if self.mode in "aw":
                self.fileobj.write(NUL * (BLOCKSIZE * 2))
                self.offset += (BLOCKSIZE * 2)
                # fill up the end with zero-blocks
                # (like option -b20 for tar does)
                blocks, remainder = divmod(self.offset, RECORDSIZE)
                if remainder > 0:
                    self.fileobj.write(NUL * (RECORDSIZE - remainder))
        finally:
            if not self._extfileobj:
                self.fileobj.close()

    def getmember(self, name):
        """Return a TarInfo3 object for member `name'. If `name' can not be
           found in the archive, KeyError is raised. If a member occurs more
           than once in the archive, its last occurrence is assumed to be the
           most up-to-date version.
        """
        tarinfo = self._getmember(name)
        if tarinfo is None:
            raise KeyError("filename %r not found" % name)
        return tarinfo

    def getmembers(self):
        """Return the members of the archive as a list of TarInfo3 objects. The
           list has the same order as the members in the archive.
        """
        self._check()
        if not self._loaded:    # if we want to obtain a list of
            self._load()        # all members, we first have to
                                # scan the whole archive.
        return self.members

    def extractfile(self, member):
        """Extract a member from the archive as a file object. `member' may be
           a filename or a TarInfo3 object. If `member' is a regular file or a
           link, an io.BufferedReader object is returned. Otherwise, None is
           returned.
        """
        self._check("r")

        if isinstance(member, str):
            tarinfo = self.getmember(member)
        else:
            tarinfo = member

        if tarinfo.isreg() or tarinfo.type not in SUPPORTED_TYPES:
            # Members with unknown types are treated as regular files.
            return self.fileobject(self, tarinfo)

        elif tarinfo.islnk() or tarinfo.issym():
            if isinstance(self.fileobj, _Stream3):
                # A small but ugly workaround for the case that someone tries
                # to extract a (sym)link as a file-object from a non-seekable
                # stream of tar blocks.
                raise StreamError("cannot extract (sym)link as file object")
            else:
                # A (sym)link's file object is its target's file object.
                return self.extractfile(self._find_link_target(tarinfo))
        else:
            # If there's no data associated with the member (directory, chrdev,
            # blkdev, etc.), return None instead of a file object.
            return None

    #--------------------------------------------------------------------------
    def next(self):
        """Return the next member of the archive as a TarInfo3 object, when
           TarFile3 is opened for reading. Return None if there is no more
           available.
        """
        self._check("ra")
        if self.firstmember is not None:
            m = self.firstmember
            self.firstmember = None
            return m

        # Advance the file pointer.
        if self.offset != self.fileobj.tell():
            self.fileobj.seek(self.offset - 1)
            if not self.fileobj.read(1):
                raise ReadError("unexpected end of data")

        # Read the next block.
        tarinfo = None
        while True:
            try:
                tarinfo = self.tarinfo.fromtarfile(self)
            except EOFHeaderError as e:
                if self.ignore_zeros:
                    self._dbg(2, "0x%X: %s" % (self.offset, e))
                    self.offset += BLOCKSIZE
                    continue
            except InvalidHeaderError as e:
                if self.ignore_zeros:
                    self._dbg(2, "0x%X: %s" % (self.offset, e))
                    self.offset += BLOCKSIZE
                    continue
                elif self.offset == 0:
                    raise ReadError(str(e))
            except EmptyHeaderError:
                if self.offset == 0:
                    raise ReadError("empty file")
            except TruncatedHeaderError as e:
                if self.offset == 0:
                    raise ReadError(str(e))
            except SubsequentHeaderError as e:
                raise ReadError(str(e))
            break

        if tarinfo is not None:
            self.members.append(tarinfo)
        else:
            self._loaded = True

        return tarinfo

    #--------------------------------------------------------------------------
    # Little helper methods:

    def _getmember(self, name, tarinfo=None, normalize=False):
        """Find an archive member by name from bottom to top.
           If tarinfo is given, it is used as the starting point.
        """
        # Ensure that all members have been loaded.
        members = self.getmembers()

        # Limit the member search list up to tarinfo.
        if tarinfo is not None:
            members = members[:members.index(tarinfo)]

        if normalize:
            name = os.path.normpath(name)

        for member in reversed(members):
            if normalize:
                member_name = os.path.normpath(member.name)
            else:
                member_name = member.name

            if name == member_name:
                return member

    def _load(self):
        """Read through the entire archive file and look for readable
           members.
        """
        while True:
            tarinfo = self.next()
            if tarinfo is None:
                break
        self._loaded = True

    def _check(self, mode=None):
        """Check if TarFile3 is still open, and if the operation's mode
           corresponds to TarFile3's mode.
        """
        if self.closed:
            raise OSError("%s is closed" % self.__class__.__name__)
        if mode is not None and self.mode not in mode:
            raise OSError("bad operation for mode %r" % self.mode)

    def _find_link_target(self, tarinfo):
        """Find the target member of a symlink or hardlink member in the
           archive.
        """
        if tarinfo.issym():
            # Always search the entire archive.
            linkname = "/".join(filter(None, (os.path.dirname(tarinfo.name), tarinfo.linkname)))
            limit = None
        else:
            # Search the archive before the link, because a hard link is
            # just a reference to an already archived file.
            linkname = tarinfo.linkname
            limit = tarinfo

        member = self._getmember(linkname, tarinfo=limit, normalize=True)
        if member is None:
            raise KeyError("linkname %r not found" % linkname)
        return member

    def __iter__(self):
        """Provide an iterator object.
        """
        if self._loaded:
            return iter(self.members)
        else:
            return TarIter3(self)

    def _dbg(self, level, msg):
        """Write debugging output to sys.stderr.
        """
        if level <= self.debug:
            #print(msg, file=sys.stderr)
            print(msg >> sys.stderr) #to get python 2.7 working, not sure if correct though...

    def __enter__(self):
        self._check()
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            self.close()
        else:
            # An exception occurred. We must not call close() because
            # it would try to write end-of-archive blocks and padding.
            if not self._extfileobj:
                self.fileobj.close()
            self.closed = True
# class TarFile3

#-------------------------------------------------------------------------------


################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################

#-------------------------------------------------------------------------------


#===============================================================================
# function to print random fun fact
#===============================================================================

def printFunFact():
    fun_facts_cosmos = [
    "1. Mercury & Venus are the only 2 planets in our solar system that have no moons.", 
    "2. If a star passes too close to a black hole, it can be torn apart.", 
    "3. The hottest planet in our solar system is Venus.", 
    "4. Our solar system is 4.6 billion years old.", 
    "5. Enceladus, one of Saturn's smaller moons, reflects 90% of the Sun's light.", 
    "6. The highest mountain discovered is the Olympus Mons, which is located on Mars.", 
    "7. The Whirlpool Galaxy (M51) was the first celestial object identified as being spiral.", 
    "8. A light-year is the distance covered by light in a single year.", 
    "9. The Milky Way galaxy is 105,700 light-years wide.", 
    "10. The Sun weighs about 330,000 times more than Earth.", 
    "11. Footprints left on the Moon won't disappear as there is no wind.", 
    "12. Because of lower gravity, a person who weighs 220 lbs on Earth would weigh 84 lbs on Mars.", 
    "13. There are 79 known moons orbiting Jupiter.", 
    "14. The Martian day is 24 hours 39 minutes and 35 seconds long.", 
    "15. NASA's Crater Observation and Sensing Satellite (LCROSS) found evidence of water on the Earth's Moon.", 
    "16. The Sun makes a full rotation once every 25 - 35 days.", 
    "17. Earth is the only planet not named after a God.", 
    "18. Due to the Sun and Moon's gravitational pull, we have tides.", 
    "19. Pluto is smaller than the United States.", 
    "20. According to mathematics, white holes are possible, although as of yet we have found none.", 
    "21. There are more volcanoes on Venus than any other planet in our solar system.", 
    "22. Uranus' blue glow is due to the gases in its atmosphere.", 
    "23. In our solar system that are 4 planets known as gas giants: Jupiter, Saturn, Uranus & Neptune.", 
    "24. Uranus has 27 moons that have been discovered so far.", 
    "25. Because of its unique tilt, a season on Uranus is equivalent to 21 Earth years.", 
    "26. Neptune's moon, Triton, orbits the planet backwards.", 
    "27. Triton is gradually getting closer to the planet it orbits.", 
    "28. There are more stars in space than there are grains of sand in the world.", 
    "29. Neptune takes nearly 165 Earth years to make one orbit of the Sun.", 
    "30. Pluto's largest moon, Charon, is half the size of Pluto.", 
    "31. The International Space Station is the largest manned object ever sent into space.", 
    "32. A day on Pluto is lasts for 153.6 hours long.", 
    "33. Saturn is the second largest planet in our solar system.", 
    "34. Any free-moving liquid in outer space will form itself into a sphere.", 
    "35. Mercury, Venus, Earth & Mars are known as the \"Inner Planets\".", 
    "36. We know more about Mars and our Moon than we do about our oceans.", 
    "37. The Black Arrow is the only British satellite to be launched using a British rocket.", 
    "38. Only 5% of the universe is visible from Earth.", 
    "39. Light travels from the Sun to the Earth in less than 10 minutes.", 
    "40. At any given moment, there are at least 2,000 thunderstorms happening on Earth.", 
    "41. The Earth's rotation is slowing slightly as time goes on.", 
    "42. If you were driving at 75 miles per hour, it would take 258 days to drive around Saturn's rings.", 
    "43. Outer Space is only 62 miles away.", 
    "44. The International Space Station circles Earth every 92 minutes.", 
    "45. Stars twinkle because of the way light is disrupted as it passes through Earth's atmosphere.", 
    "46. We always see the same side of the Moon, no matter where we stand on Earth.", 
    "47. There are three main types of galaxies: elliptical, spiral & irregular.", 
    "48. There are approximately 100 thousand million stars in the Milky Way.", 
    "49. Using the naked eye, you can see 3 - 7 different galaxies from Earth.", 
    "50. In 2016, scientists detected a radio signal from a source 5 billion light-years away.", 
    "51. The closest galaxy to us is the Andromeda Galaxy  its estimated at 2.5 million light-years away.", 
    "52. The first Supernovae observed outside of our own galaxy was in 1885.", 
    "53. The first ever black hole photographed is 3 million times the size of Earth.", 
    "54. The distance between the Sun & Earth is defined as an Astronomical Unit.", 
    "55. The second man on the moon was Buzz Aldrin. \"Moon\" was Aldrin's mother's maiden name.", 
    "56. Buzz Aldrin's birth name was Edwin Eugene Aldrin Jr.", 
    "57. On Venus, it snows metal and rains sulfuric acid.", 
    "58. The Mariner 10 was the first spacecraft that visited Mercury in 1974.", 
    "59. Space is completely silent.", 
    "60. Coca-Cola was the first commercial soft drink that was ever consumed in space.", 
    "61. Astronauts can grow approximately two inches (5 cm) in height when in space.", 
    "62. The Kuiper Belt is a region of the Solar System beyond the orbit of Neptune.", 
    "63. The first woman in space was a Russian called Valentina Tereshkova.", 
    "64. If Saturn's rings were 3 feet long, they would be 10,000 times thinner than a razorblade.", 
    "65. The Hubble Space Telescope is one of the most productive scientific instruments ever built.", 
    "66. The first artificial satellite in space was called \"Sputnik\".", 
    "67. Exoplanets are planets that orbit around other stars.", 
    "68. The center of the Milky Way smells like rum & tastes like raspberries.", 
    "69. Our moon is moving away from Earth at a rate of 1.6 inch (4 cm) per year!", 
    "70. Pluto is named after the Roman god of the underworld, not the Disney Dog.", 
    "71. Spacesuit helmets have a Velcro patch, to help astronauts itch.", 
    "72. The ISS is visible to more than 90% of the Earth's population.", 
    "73. Saturn is the only planet that could oat in water.", 
    "74. Asteroids are the byproducts of formations in the solar system, more than 4 billion years ago.", 
    "75. Astronauts can't burp in space.", 
    "76. Uranus was originally called \"George's Star\".", 
    "77. A sunset on Mars is blue.", 
    "78. The Earth weighs about 81 times more than the Moon.", 
    "79. The first living mammal to go into space was a dog named \"Laika\" from Russia.", 
    "80. The word \"astronaut\" means \"star sailor\" in its origins.", 
    "81. \"NASA\" stands for National Aeronautics and Space Administration.", 
    "82. Gennady Padalka has spent more time in space than anyone else.", 
    "83. Mercury has no atmosphere, which means there is no wind or weather.", 
    "84. In China, the Milky Way is known as the \"Silver River\".", 
    "85. Red Dwarf stars that are low in mass can burn continually for up to 10 trillion years!", 
    "86. Scientists once believed that the same side of Mercury always faced the Sun.", 
    "87. Jupiter's Red Spot is shrinking.", 
    "88. A large percentage of asteroids are pulled in by Jupiter's gravity.", 
    "89. A day on Mercury is equivalent to 58 Earth days.", 
    "90. As space has no gravity, pens won't work.", 
    "91. On average it takes the light only 1.3 seconds to travel from the Moon to Earth.", 
    "92. There are 88 recognized star constellations in our night sky.", 
    "93. The center of a comet is called a \"nucleus\".", 
    "94. As early as 240BC the Chinese began to document the appearance of Halley's Comet.", 
    "95. In 2006, the International Astronomical Union reclassified Pluto as a dwarf planet.", 
    "96. There are 5 Dwarf Planets recognized in our Solar System.", 
    "97. Mars is the most likely planet in our solar system to be hospitable to life.", 
    "98. Halley's Comet will pass over Earth again on 26th July 2061.", 
    "99. There is a planet half the radius of the Earth with a surface made up of diamonds.", 
    "100. Buzz Lightyear from Toy Story has actually been to outer space!"]
    print("\nDid you know?\nFun Fact: #%s" % fun_facts_cosmos[random.randint(0, 99)])

#-------------------------------------------------------------------------------


#==============================================================================#
#                                                                              #
#                                  MAIN CODE                                   #
#                                                                              #
#==============================================================================#

#-------------------------------------------------------------------------------


#===============================================================================
# utility functions
#===============================================================================

def printSelectedFile(pathToFile, name, modified):
    nameLength = len(name)
    print('\n\n\
========' + nameLength*'=' + '\n\
=== %s ===\n\
========' % (name) + nameLength*'=' + '\n%s' % (pathToFile))
    print('modified: %s\n' % modified)


def printCustomMessage(name):
    nameLength = len(name)
    print('\n\n\
========' + nameLength*'=' + '\n\
=== %s ===\n\
========' % (name) + nameLength*'=')


def isTarfileGood(pathToFileInRes):
    try:
        if PYTHON_MAJOR == 2:
            tar = TarFile2.open(pathToFileInRes, 'r') # using local copy of tarfile library 2.7 branch
        elif PYTHON_MAJOR == 3 and PYTHON_MINOR < 6:
            tar = TarFile3.open(pathToFileInRes, 'r') # using local copy of tarfile library 3.4 branch
        else:
            tar = tarfile.open(pathToFileInRes, 'r') # using imported tarfile library
        try:
            tar.getmembers()
            tar.close()
            return True
        #except (tarfile.TarError) as e:
        except (TarError) as e: # using local copy of tarfile library
            #print("\nTarfile corrupted ERROR: isTarfileGood(e1) %s in:\n%s" % (e, pathToFileInRes))
            return False
        finally:
            tar.close()
    except (Exception) as e:
        #print("\nTarfile ERROR: isTarfileGood(e2) %s in:\n%s" % (e, pathToFileInRes))
        return False


def setPermissions755(tarinfo):
    if not re.search(r'(.*.(tar|tar.gz|tar.bz2|tar.xz|tgz|tbz|txz|bin|run))', tarinfo.name):
        tarinfo.mode |= 0o755
    return tarinfo


def extractTarfile(pathToDir, pathToFileInRes):
    print("\n\nextracting tarfile...")
    try:
        tar = tarfile.open(pathToFileInRes, 'r:', format = GNU_FORMAT, encoding = "utf-8")
        try:

            updatedMembers = []
            for tarinfo in tar.getmembers():
                tarinfo = setPermissions755(tarinfo)
                updatedMembers.append(tarinfo)
            tar.extractall(members = updatedMembers, path = pathToDir)

            tar.close()
        except (tarfile.TarError) as e:
            print("\nTarfile extraction ERROR: extractTarfile(e1) %s in:\n%s" % (e, pathToFileInRes))
            pressEnterToExit()
        finally:
            tar.close()
    except (Exception) as e:
        print("\nTarfile extraction ERROR: extractTarfile(e2) %s in:\n%s" % (e, pathToFileInRes))
        pressEnterToExit()


def createTarfile(pathToDir, fileName):
    print("\ncreating new tarfile...")
    try:
        tar = tarfile.open(fileName, 'w:', format = GNU_FORMAT, encoding = "utf-8")
        try:

            if((PYTHON_MAJOR == 2 and PYTHON_MINOR >= 7)
            or (PYTHON_MAJOR == 3 and PYTHON_MINOR >= 2)
            or (PYTHON_MAJOR >= 3)):
                for item in listDirectory(pathToDir):
                    tar.add(os.path.join(pathToDir, item), arcname = item, filter = setPermissions755)
            else:
                for file in listDirsRecursively(pathToDir):
                    pathToFile = os.path.join(pathToDir, file)
                    tarinfo = tar.gettarinfo(pathToFile, arcname = file)
                    tarinfo = setPermissions755(tarinfo)
                    try:
                        f = open(pathToFile, 'rb')
                        try:
                            tar.addfile(tarinfo, fileobj = f)
                            f.close()
                        except (OSError, IOError) as e:
                            print("\nTarfile creation ERROR: createTarfile(e1) %s in:\n%s" % (e, fileName))
                        finally:
                            f.close()
                    except (Exception) as e:
                        print("\nTarfile creation ERROR: createTarfile(e2) %s in:\n%s" % (e, fileName))

            tar.close()
        except (tarfile.TarError) as e:
            print("\nTarfile creation ERROR: createTarfile(e3) %s in:\n%s" % (e, fileName))
            pressEnterToExit()
        finally:
            tar.close()
    except (Exception) as e:
        print("\nTarfile creation ERROR: createTarfile(e4) %s in:\n%s" % (e, fileName))
        pressEnterToExit()


def createDir(pathToDir):
    if not os.path.exists(pathToDir):
        try:
            os.mkdir(pathToDir)
        except (OSError) as e:
            print("\nDirectory creation ERROR: createDir(e1) %s - %s" % (e.filename, e.strerror))
        except (Exception) as e:
            print("\nDirectory creation ERROR: createDir(e2) %s" % (e))


def removeDir(pathToDir):
    if os.path.exists(pathToDir):
        try:
            shutil.rmtree(pathToDir)
        except (shutil.Error, OSError, IOError, Exception) as e:
            print("\nDirectory removal ERROR: removeDir(e) %s" % (e))


def moveFile(pathFrom, pathTo):
    try:
        shutil.move(pathFrom, pathTo)
    except (OSError) as e:
        print("\nFile move ERROR: moveFile(e1) %s - %s" % (e.filename, e.strerror))
    except (Exception) as e:
        print("\nFile move ERROR: moveFile(e2) %s" % (e))


def renameFile(pathToFileOld, pathToFileNew):
    try:
        os.rename(pathToFileOld, pathToFileNew)
    except (OSError) as e:
        print("\nFile rename ERROR: renameFile(e1) %s - %s" % (e.filename, e.strerror))
        pressEnterToExit()
    except (Exception) as e:
        print("\nFile rename ERROR: renameFile(e2) %s" % (e))
        pressEnterToExit()


def removeFile2(pathToDir, fileName):
    try:
        os.remove(os.path.join(pathToDir, fileName))
        print("\n%s\t deleted from:\t%s" % (fileName, pathToDir))
    except (OSError) as e:
        print("\nFile remove ERROR: removeFile2(e1) %s - %s" % (e.filename, e.strerror))
    except (Exception) as e:
        print("\nFile remove ERROR: removeFile2(e2) %s" % (e))


def removeFile(pathToFile):
    pathToDir = os.path.dirname(pathToFile)
    fileName = os.path.basename(pathToFile)
    try:
        os.remove(pathToFile)
        print("%s\t deleted from:\t%s" % (fileName, pathToDir))
    except (OSError) as e:
        print("\nFile remove ERROR: removeFile(e1) %s - %s" % (e.filename, e.strerror))
    except (Exception) as e:
        print("\nFile remove ERROR: removeFile(e2) %s" % (e))


def listDirectory(pathToDir):
    listDir = []
    try:
        pathToDir = os.path.normpath(pathToDir)
        listDir = os.listdir(pathToDir)
    except (OSError) as e:
        print("\nDirectory listing ERROR: listDirectory(e1) %s - %s" % (e.filename, e.strerror))
        pressEnterToExit()
    except (Exception) as e:
        print("\nDirectory listing ERROR: listDirectory(e2) %s" % (e))
        pressEnterToExit()
    return listDir


def listDirs(pathBase, pathLocal, filesList):
    pathToDir = os.path.join(pathBase, pathLocal)
    for item in listDirectory(pathToDir):
        pathToItem = os.path.join(pathToDir, item)
        pathToItemLocal = os.path.join(pathLocal, item) #to create list of paths to files without the very first base folder - it is used to create tarballs
        if os.path.isdir(pathToItem):
            listDirs(pathBase, pathToItemLocal, filesList)
        else:
            filesList.append(pathToItemLocal)


def listDirsRecursively(pathBase):
    filesList = []
    localPath = ''
    listDirs(pathBase, localPath, filesList)
    return filesList


def getDateFromNahkaFileName(fileMatcher): #valid, but not being used anymore after refactor
    return lambda f : fileMatcher.sub(r'\3', f)


def getLastModificationTime(pathToFile):
    secondsSinceEpoch = 0
    try:
        secondsSinceEpoch = os.path.getmtime(pathToFile)
    except (OSError) as e:
        print("\nGetting file info ERROR: getLastModificationTime(e) %s - %s" % (e.filename, e.strerror))
    return secondsSinceEpoch


def getLastModificationTimeAsString(pathToFile):
    return time.ctime(getLastModificationTime(pathToFile))


def getFileSize(pathToFile):
    fileSize = 1
    try:
        fileSize = os.stat(pathToFile).st_size
    except (OSError, IOError, Exception) as e:
        print("\nGetting file info ERROR: getFileSize(e) %s" % (e))
    if fileSize <= 0:
        fileSize = 1
    return fileSize


def checkIfSymlinkAndGetRelativePath(pathToFile):
    if os.path.islink(pathToFile):
        pathtoDir = os.path.dirname(pathToFile)
        pathInSymlink = os.readlink(pathToFile)
        pathToFile = os.path.normpath(os.path.join(pathtoDir, pathInSymlink))
#### OR simply:
        #pathToFile = os.path.realpath(pathToFile)

        if not os.path.isfile(pathToFile):
            print("file that is being pointed to by symlink does not exist anymore: %s" % pathFromSymlink)
    return pathToFile

#-------------------------------------------------------------------------------


#===============================================================================
# functions to print progress bar
#===============================================================================

def getUnit(variable):
    try:
        units = ['kB', 'MB', 'GB', 'TB'] #Decimal Prefixes - The SI standard http://wolfprojects.altervista.org/articles/binary-and-decimal-prefixes/
        variableUnit = ' B'
        for unit in units:
            if variable >= 1000:
                variable /= 1000
                variableUnit = unit
            else:
                break
        #which translates to:
        # i = 0
        # while variable >= 1000 and i < len(units):
            # variable /= 1000
            # variableUnit = units[i] #"damn I miss array[i++] style syntax" - Dawid Koszewski, AD 2019
            # i += 1
    except (Exception) as e:
        print("\nProgress bar ERROR: getUnit(e) %s" % (e))
    return variable, variableUnit


def printProgressBar(copied, fileSize, speedCurrent = 1000000.0, speedAverage = 1000000.0):
    try:
        percent = (copied / (fileSize * 1.0)) # multiplication by 1.0 needed for python 2
        if percent > 1.0:
            percent = 1.0
        dataLeft = (fileSize - copied) #Bytes
        timeLeftSeconds = (dataLeft / speedAverage) #Seconds
        timeLeftHours = (timeLeftSeconds / 3600)
        timeLeftSeconds = (timeLeftSeconds % 3600)
        timeLeftMinutes = (timeLeftSeconds / 60)
        timeLeftSeconds = (timeLeftSeconds % 60)

        #padding = len(str(int(fileSize)))
        copied, copiedUnit = getUnit(copied)
        fileSize, fileSizeUnit = getUnit(fileSize)
        speedCurrent, speedCurrentUnit = getUnit(speedCurrent)

        symbolDone = '='
        symbolLeft = '-'
        sizeTotal = 20
        sizeDone = int(percent * sizeTotal)

        sizeLeft = sizeTotal - sizeDone
        progressBar = '[' + sizeDone*symbolDone + sizeLeft*symbolLeft + ']'
        sys.stdout.write('\r%3d%% %s [%3.1d%s/%3.1d%s]  [%6.2f%s/s] %3.1dh%2.2dm%2.2ds' % (percent*100, progressBar, copied, copiedUnit, fileSize, fileSizeUnit, speedCurrent, speedCurrentUnit, timeLeftHours, timeLeftMinutes, timeLeftSeconds))
        sys.stdout.flush()
        #time.sleep(0.05) #### DELETE AFTER DEVELOPMENT ##########################################################################################################
    except (Exception) as e:
        print("\nProgress bar ERROR: printProgressBar(e) %s" % (e))


def handleProgressBarWithinLoop(vars, buffer, fileSize):
    try:
    #------------------------------------------
    # less readable and probably slower version
    #------------------------------------------
        # vars['timeNow'] = time.time()
        # vars['timeNowData'] += len(buffer)
    # #update Current Speed
        # if vars['timeNow'] >= (vars['timeMark'] + vars['time_step']):
            # vars['timeDiff'] = vars['timeNow'] - vars['timeMark']
            # if vars['timeDiff'] == 0:
                # vars['timeDiff'] = 0.1
            # vars['dataDiff'] = vars['timeNowData'] - vars['timeMarkData']
            # vars['timeMark'] = vars['timeNow']
            # vars['timeMarkData'] = vars['timeNowData']
            # vars['speedCurrent'] = (vars['dataDiff'] / vars['timeDiff']) #Bytes per second
    # #update Average Speed and print progress
        # if vars['timeNowData'] >= (vars['dataMark'] + vars['data_step']):
            # vars['timeDiff'] = vars['timeNow'] - vars['timeStarted']
            # if vars['timeDiff'] == 0:
                # vars['timeDiff'] = 0.1
            # vars['dataMark'] = vars['timeNowData']
            # vars['speedAverage'] = (vars['timeNowData'] / vars['timeDiff']) #Bytes per second
    # except (Exception) as e:
        # print("\nProgress bar ERROR: handleProgressBarWithinLoop(e) %s" % (e))
    # #print progress
    # printProgressBar(vars['timeNowData'], fileSize, vars['speedCurrent'], vars['speedAverage'])


    #------------------------------------------
    # more readable and probably faster version
    #------------------------------------------

    #----------------------------
    # get values from list
    #----------------------------
        timeStarted     = vars[0]
        data_step       = vars[1]
        dataMark        = vars[2]
        time_step       = vars[3]
        timeMark        = vars[4]
        timeMarkData    = vars[5]
        timeNow         = vars[6]
        timeNowData     = vars[7]
        speedCurrent    = vars[8]
        speedAverage    = vars[9]
    #----------------------------

        timeNow = time.time()
        timeNowData += len(buffer)
    #update Current Speed
        if timeNow >= (timeMark + time_step):
            timeDiff = timeNow - timeMark
            if timeDiff == 0:
                timeDiff = 0.1
            dataDiff = timeNowData - timeMarkData
            timeMark = timeNow
            timeMarkData = timeNowData
            speedCurrent = (dataDiff / timeDiff) #Bytes per second
    #update Average Speed and print progress
        if timeNowData >= (dataMark + data_step):
            timeDiff = timeNow - timeStarted
            if timeDiff == 0:
                timeDiff = 0.1
            dataMark = timeNowData
            speedAverage = (timeNowData / timeDiff) #Bytes per second

    #----------------------------
    # update list
    #----------------------------
        vars[2] = dataMark
        vars[4] = timeMark
        vars[5] = timeMarkData
        vars[6] = timeNow
        vars[7] = timeNowData
        vars[8] = speedCurrent
        vars[9] = speedAverage
    #----------------------------

    except (Exception) as e:
        print("\nProgress bar ERROR: handleProgressBarWithinLoop(e) %s" % (e))
    #print progress
    printProgressBar(timeNowData, fileSize, speedCurrent, speedAverage)


def initProgressBarVariables():
    try:
        # progressBarVars = {}

        # progressBarVars['timeStarted'] = time.time()
        # progressBarVars['data_step'] = 131072
        # progressBarVars['dataMark'] = 0

        # progressBarVars['time_step'] = 1.0
        # progressBarVars['timeMark'] = time.time()
        # progressBarVars['timeMarkData'] = 0
        # progressBarVars['timeNow'] = 0.0
        # progressBarVars['timeNowData'] = 0
        # progressBarVars['speedCurrent'] = 1048576.0
        # progressBarVars['speedAverage'] = 1048576.0

        progressBarVars = [1.0] * 10

        timeStarted = time.time()
        data_step = 256*1024
        dataMark = 0

        time_step = 1.0
        timeMark = time.time()
        timeMarkData = 0
        timeNow = 0.0
        timeNowData = 0
        speedCurrent = 1000*1000.0
        speedAverage = 1000*1000.0

        progressBarVars[0] = timeStarted
        progressBarVars[1] = data_step
        progressBarVars[2] = dataMark
        progressBarVars[3] = time_step
        progressBarVars[4] = timeMark
        progressBarVars[5] = timeMarkData
        progressBarVars[6] = timeNow
        progressBarVars[7] = timeNowData
        progressBarVars[8] = speedCurrent
        progressBarVars[9] = speedAverage

    except (Exception) as e:
        print("\nProgress bar ERROR: initProgressBarVariables(e) %s" % (e))
    return progressBarVars

#-------------------------------------------------------------------------------


#===============================================================================
# functions to calculate checksum and get new file name
#===============================================================================

def getNewChecksumFileName(fileName, fileMatcher, checksumAsHex):
    fileNameNew = ""
    fileNamePrepend = fileMatcher.sub(r'\1', fileName)
    fileNameAppend = fileMatcher.sub(r'\3', fileName)
    checksumAsHexUpper = checksumAsHex.upper()
    fileNameNew = fileNamePrepend + checksumAsHexUpper + fileNameAppend
    return fileNameNew


def getChecksumAsHex(checksum):
    #checksumFormatted = '0x' + hex(checksum)[2:] #in python 2.7.14 it appends letter L
    checksumHex = "%x" % checksum
    return checksumHex.zfill(8)


def getChecksum(pathToFile):
    checksum = 1 #initialize with 1
    if os.path.isfile(pathToFile):
        try:
            f = open(pathToFile, 'rb')
            print("\ncalculating checksum...")
            fileSize = getFileSize(pathToFile)

            try:
                progressBarVars = initProgressBarVariables()

                while 1:
                    buffer = f.read(1024*1024) #default 64*1024 for linux (SLOW), 1024*1024 for windows (FAST also on linux)
                    if not buffer:
                        break
                    checksum = adler32_function(buffer, checksum)

                    handleProgressBarWithinLoop(progressBarVars, buffer, fileSize)
                printProgressBar(progressBarVars[7], fileSize, progressBarVars[8], progressBarVars[9])
                print()

                f.close()
                checksum = checksum & 0xffffffff
            except (OSError, IOError) as e:
                print("\nCalculate checksum ERROR: getChecksum(e1) %s - %s" % (e.filename, e.strerror))
            finally:
                f.close()
        except (Exception) as e:
            print ("\nCalculate checksum ERROR: getChecksum(e2) %s" % (e))
    else:
        print('\nERROR: getChecksum(e3) Could not find file to calculate checksum')
    return checksum

#-------------------------------------------------------------------------------


#===============================================================================
# functions to modify Stratix file with customized nahka file
#===============================================================================

def replaceFileInArtifacts(pathToDirTempArtifacts, pathToFileInRes, fileMatcher):
    listDirTempArtifacts = listDirectory(pathToDirTempArtifacts)
    for tempFileArtifacts in listDirTempArtifacts:
        if fileMatcher.search(tempFileArtifacts):
            removeFile2(pathToDirTempArtifacts, tempFileArtifacts)
    try:
        shutil.copy2(pathToFileInRes, pathToDirTempArtifacts)
        print("%s\t copied to:\t%s" % (os.path.basename(pathToFileInRes), pathToDirTempArtifacts))
    except (shutil.Error, OSError, IOError, Exception) as e:
        print("\nFile copy ERROR: replaceFileInArtifacts(e) %s" % (e))
        pressEnterToExit()


def modifyFileContent(pathToFile, modifier_callback):
#------------------------------------------
# open file
#------------------------------------------
    fileContent = None
    try:
        # if PYTHON_MAJOR >= 3:
            # f = open(pathToFile, 'r', newline = '')
        # else:
            # f = open(pathToFile, 'rb')
        f = open(pathToFile, 'r')
        try:
            fileContent = f.read()
            f.close()

        except (OSError, IOError) as e:
            print("\nInstaller script reading ERROR: setNewFileNameInInstallerScripts(e1) %s - %s" % (e.filename, e.strerror))
        finally:
            f.close()
    except (Exception) as e:
        print("\nInstaller script reading ERROR: setNewFileNameInInstallerScripts(e2) %s" % (e))

#------------------------------------------
# modify file
#------------------------------------------
    fileContent = modifier_callback(fileContent)

#------------------------------------------
# save file
#------------------------------------------
    try:
        if PYTHON_MAJOR >= 3:
            f = open(pathToFile, 'w', newline = '')
        else:
            f = open(pathToFile, 'wb')
        try:
            f.write(fileContent)
            f.close()
        except (OSError, IOError) as e:
            print("\nInstaller script writing ERROR: setNewFileNameInInstallerScripts(e3) %s - %s" % (e.filename, e.strerror))
        finally:
            f.close()
    except (Exception) as e:
        print("\nInstaller script writing ERROR: setNewFileNameInInstallerScripts(e4) %s" % (e))


def setNewFileNameInInstallerScripts(pathToDirTemp, pathToFileInRes, fileMatcherInstaller, fileMatcher):
    fileName = os.path.basename(pathToFileInRes)
    listDirTemp = listDirectory(pathToDirTemp)
    for tempFile in listDirTemp:
        tempFilePath = os.path.join(pathToDirTemp, tempFile)
        if os.path.isfile(tempFilePath):
            if fileMatcherInstaller.search(tempFile):
                # modify with new nahka filename
                modifyFileContent(tempFilePath, lambda fileContent : fileMatcher.sub((r'\1%s\5' % (fileName)), fileContent))
                print("%s\t updated in:\t%s" % (fileName, tempFilePath))


def renameStratixFile(fileNameTemp, fileNameNew):
    renameFile(fileNameTemp, fileNameNew)
    if os.path.isfile(fileNameNew) and os.path.getsize(fileNameNew) > 0:
        modified = getLastModificationTimeAsString(fileNameNew)
        printSelectedFile(fileNameNew, 'new Stratix file', modified)
    else:
        print("\nSomething went wrong. New Stratix file not generated correctly...")
        print("\nPlease manually check file: %s" % (fileNameTemp))

#-------------------------------------------------------------------------------


#===============================================================================
# custom implementation of copyfileobj from shutil LIBRARY (to enable displaying progress bar)
#===============================================================================

def copyfileobj(fsrc, fdst, src, length = 1024*1024): #default 64*1024 for linux
    fileSize = getFileSize(src)

    progressBarVars = initProgressBarVariables()

    while 1:
        buffer = fsrc.read(length)
        if not buffer:
            break
        fdst.write(buffer)

        handleProgressBarWithinLoop(progressBarVars, buffer, fileSize)
    printProgressBar(progressBarVars[7], fileSize, progressBarVars[8], progressBarVars[9])
    print()

#-------------------------------------------------------------------------------


#===============================================================================
# functions to get paths to latest Nahka and Stratix files and copy / download them
#===============================================================================

#-------------------------------------------------------------------------------
# "get file" final workers
#-------------------------------------------------------------------------------
def getFileFromLocalNetwork(pathToFile, pathToDirRes, pathToFileInRes):
    print("copying file to: %s" % (pathToDirRes))
    try:
        #shutil.copy2(pathToFile, pathToDirRes)
        copy2(pathToFile, pathToFileInRes)
    except (shutil.Error, OSError, IOError, Exception) as e:
        print("\nFile copy ERROR: getFileFromLocalNetwork(e) %s" % (e))
        pressEnterToExit()
    return pathToFileInRes


def getFileFromArtifactory(pathToFile, pathToDirRes, pathToFileInRes):
    import requests
    try:
        response = requests.get(pathToFile, stream = True)
        response.raise_for_status()
        print("downloading file to: %s" % pathToDirRes)
        fileSize = int(response.headers['Content-length'])
        if fileSize <= 0:
            fileSize = 1
        try:
            f = open(pathToFileInRes, 'wb')

            try:
                progressBarVars = initProgressBarVariables()

                while 1:
                    buffer = response.raw.read(1024) #default 128
                    if not buffer:
                        break
                    f.write(buffer)

                    handleProgressBarWithinLoop(progressBarVars, buffer, fileSize)
                printProgressBar(progressBarVars[7], fileSize, progressBarVars[8], progressBarVars[9])
                print()

                f.close()
            except (OSError, IOError) as e:
                print("\nFile download ERROR: getFileFromArtifactory(e1) %s - %s" % (e.filename, e.strerror))
                pressEnterToExit()
            finally:
                f.close()
        except (Exception) as e:
            print("\nFile download ERROR: getFileFromArtifactory(e2) %s" % (e))
            pressEnterToExit()
    except (requests.exceptions.HTTPError, requests.exceptions.RequestException, Exception) as e:
        print("\nFile download ERROR: getFileFromArtifactory(e3) %s" % (e))
        pressEnterToExit()
    return pathToFileInRes


def getFileFromServer(serverAddressAndPath, pathToDirRes, imageMatcher, fileMatcher, messagePrinted):
    fileName = ""
    if fileMatcher.search(serverAddressAndPath):
        fileName = fileMatcher.sub(r'\2\3\4\5', serverAddressAndPath)
        serverAddressAndPathToDir = fileMatcher.sub(r'\1', serverAddressAndPath)
    else:
        serverAddressAndPathToDir = serverAddressAndPath
    serverAddress, pathToDir = serverAddressAndPathToDir.split(':')
    if not pathToDir.endswith('/'):
        pathToDir = pathToDir + '/'
    try:
        print("\n\ngetting %s file from other server..." % (messagePrinted))
        sftp = subprocess.Popen(['sftp', '%s' % serverAddress], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1)
        sftp.stdin.write(b'cd %s\n' % pathToDir)
        sftp.stdin.flush()
        sftp.stdout.readline()
        sftp.stdout.flush()
        if not fileName:
            sftp.stdin.write(b'ls -t1 %s | head -1\n' % (imageMatcher))
            sftp.stdin.flush()
            sftp.stdout.readline()
            sftp.stdout.flush()
            fileName = sftp.stdout.readline().decode(sys.stdout.encoding).strip()
            sftp.stdout.flush()
        sftp.communicate(b'get %s%s' % (pathToDir, fileName))[0].decode(sys.stdout.encoding)
        sftp.stdin.close()
        sftp.stdout.close()
    except (Exception) as e:
        print("\nFile download through sftp ERROR: getFileFromServer(e1) %s" % (e))
        pressEnterToExit()
    if os.path.isfile(fileName) and os.path.getsize(fileName) > 0:
        pathToFileInRes = os.path.join(pathToDirRes, fileName)
        moveFile(fileName, pathToFileInRes)
    else:
        print("\nFile download ERROR: getFileFromServer(e2) %s" % (serverAddress + ':' + pathToDir + fileName))
        pressEnterToExit()
    return pathToFileInRes

#-------------------------------------------------------------------------------
# "get file" main verifier
#-------------------------------------------------------------------------------
def getFile(pathToFile, pathToDirRes, pathToFileInRes, modified, getFileFrom_callback):
    fileIsAvailable = True if modified else False
    fileIsInResources = os.path.isfile(pathToFileInRes)
    fileIsGood = isTarfileGood(pathToFileInRes)

    if fileIsAvailable:
        if fileIsInResources:
            if fileIsGood:
                print("file already present in: %s\n" % (pathToDirRes))
            else:
                print("file already present in: %s but it is corrupted - attempting to get a fresh new copy\n" % (pathToDirRes))
                pathToFileInRes = getFileFrom_callback(pathToFile, pathToDirRes, pathToFileInRes)
        else:
            pathToFileInRes = getFileFrom_callback(pathToFile, pathToDirRes, pathToFileInRes)
    elif fileIsInResources:
        if fileIsGood:
            print("\nCould not find the file in the specified location, but the file is present in: %s\n" % (pathToDirRes))
            pressEnterToContinue()
        else:
            print("\nCould not find file in the specified location - the file is present in: %s but it is corrupted\n" % (pathToDirRes))
            pressEnterToExit()
    else:
        print("\nCould not find anything! Please specify possible file locations in the ini file...\n")
        #pressEnterToExit() #when this line is commented it can cause a little mess in directory and too many errors being printed out in console
    return pathToFileInRes

#-------------------------------------------------------------------------------
# "get file" check modification time (silent validators)
#-------------------------------------------------------------------------------
def getLastFileModificationTimeLocal(pathToFile):
    modified = ""
    if os.path.isfile(pathToFile):
        modified = getLastModificationTimeAsString(pathToFile)
    return modified


def getLastFileModificationTimeURL(pathToFile):
    modified = ""
    try:
        import requests
    except (ImportError, Exception) as e:
        print("\ngetLastFileModificationTimeURL(e1) %s" % (e))
        print("Script will now attempt to install required module")
        pressEnterToContinue()
        installRequests()
    try:
        import requests
    except (ImportError, Exception) as e:
        print("\ngetLastFileModificationTimeURL(e2) %s\nCould not get requests module from pypi.org" % (e))
        print("If you need to get Stratix or Nahka file from the web you will need to manually download it to the local directory (and add path to it in the ini file)\n")
        pressEnterToExit()
    try:
        response = requests.head(pathToFile)
        if response.status_code == (200 or 300 or 301 or 302 or 303 or 307 or 308):
            modified = response.headers['last-modified']
    except (requests.exceptions.HTTPError, requests.exceptions.RequestException, Exception) as e:
        print("\nRequest Header ERROR: getLastFileModificationTimeURL(e3) %s\nYou probably need authentication to download that file..." % (e))
    return modified

#-------------------------------------------------------------------------------
# "get file" helper handlers
#-------------------------------------------------------------------------------
def handleGettingFileFromLocalNetwork(pathToFile, pathToDirRes, fileMatcher, messagePrinted):
    fileName = os.path.basename(pathToFile)
    pathToFileInRes = os.path.join(pathToDirRes, fileName)
    modified = getLastFileModificationTimeLocal(pathToFile)
    printSelectedFile(pathToFile, ('selected %s file' % (messagePrinted)), modified)
    pathToFileInRes = getFile(pathToFile, pathToDirRes, pathToFileInRes, modified, getFileFromLocalNetwork)
    return pathToFileInRes


def handleGettingFileFromArtifactory(pathToFile, pathToDirRes, fileMatcher, messagePrinted):
    fileName = fileMatcher.sub(r'\2\3\4\5', pathToFile)
    pathToFileInRes = os.path.join(pathToDirRes, fileName)
    modified = getLastFileModificationTimeURL(pathToFile)
    printSelectedFile(pathToFile, ('selected %s file' % (messagePrinted)), modified)
    pathToFileInRes = getFile(pathToFile, pathToDirRes, pathToFileInRes, modified, getFileFromArtifactory)
    return pathToFileInRes


def handleGettingFileFromServer(pathToFile, pathToDirRes, imageMatcher, fileMatcher, messagePrinted):
    pathToFileInRes = getFileFromServer(pathToFile, pathToDirRes, imageMatcher, fileMatcher, messagePrinted) #to avoid multiple passord promts when connecting through sftp
    modified = getLastFileModificationTimeLocal(pathToFileInRes)
    printSelectedFile((pathToFile + ' --> ' + os.path.basename(pathToFileInRes)), ('selected %s file' % (messagePrinted)), modified)
    return pathToFileInRes

#-------------------------------------------------------------------------------
# "get file" path finders
#-------------------------------------------------------------------------------
def getPathToLatestFileInDir(pathToDir, fileMatcher):
    filePathsList = []
    for item in listDirectory(pathToDir):
        pathToFile = os.path.join(pathToDir, item)
        if os.path.isfile(pathToFile):
            if fileMatcher.search(item):
                filePathsList.append(pathToFile)
    comparator = getLastModificationTime
    filePathsList.sort(key = comparator, reverse = False)
    return filePathsList[-1] if filePathsList else ""


def getPathToFileUnderUrl(url, fileMatcher, messagePrinted):
    pathToFile = ""
    try:
        import requests
    except (ImportError, Exception) as e:
        print("\ngetPathToFileUnderUrl(e1) %s" % (e))
        print("Script will now attempt to install required module")
        pressEnterToContinue()
        installRequests()
    try:
        import requests
    except (ImportError, Exception) as e:
        print("\ngetPathToFileUnderUrl(e2) %s\nCould not get requests module from pypi.org" % (e))
        print("If you need to get Stratix or Nahka file from the web you will need to manually download it to the local directory (and add path to it in the ini file)\n")
        pressEnterToExit()
    try:
        response = requests.get(url, stream = True)
        if response.status_code == (200 or 300 or 301 or 302 or 303 or 307 or 308):
            responseHTML = response.text.splitlines()
            for line in responseHTML:
                line = line.strip()
                if fileMatcher.search(line):
                    fileName = fileMatcher.sub(r'\2\3\4', line)
                    if url.endswith('/'):
                        pathToFile = url + fileName
                    else:
                        pathToFile = url + '/' + fileName
                    break
        else:
            response.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.RequestException, Exception) as e:
        print("\n\ngetting %s file from artifactory..." % (messagePrinted))
        print("\nRequest Header ERROR: getPathToFileUnderUrl(e3) %s\nYou probably need authentication to download that file..." % (e))
    return pathToFile


def getPathToFileUnderUrlFromTemplate(PATH, fileMatcher, PATH_ARTIFACTORY_TEMPLATE, messagePrinted):
    urlPrepend, urlAppend = PATH_ARTIFACTORY_TEMPLATE.rsplit('*', 1)
    urlPrepend = urlPrepend.rstrip('*')
    url = urlPrepend + PATH + urlAppend
    pathToFile = getPathToFileUnderUrl(url, fileMatcher, messagePrinted)
    return pathToFile

#-------------------------------------------------------------------------------
# "get file" main handler
#-------------------------------------------------------------------------------
def handleGettingFile(pathToDirRes, serverMatcher, urlMatcher, imageMatcher, fileMatcher, PATH_ARTIFACTORY_TEMPLATE, PATH, messagePrinted):
    createDir(pathToDirRes)
    pathToFileInRes = ""
    if serverMatcher.search(PATH):
        pathToFile = PATH
        pathToFileInRes = handleGettingFileFromServer(pathToFile, pathToDirRes, imageMatcher, fileMatcher, messagePrinted)
    elif urlMatcher.search(PATH):
        pathToFile = ""
        if fileMatcher.search(PATH):
            pathToFile = PATH
        else:
            pathToFile = getPathToFileUnderUrl(PATH, fileMatcher, messagePrinted)
        pathToFileInRes = handleGettingFileFromArtifactory(pathToFile, pathToDirRes, fileMatcher, messagePrinted)
    elif PATH.isdigit():
        pathToFile = getPathToFileUnderUrlFromTemplate(PATH, fileMatcher, PATH_ARTIFACTORY_TEMPLATE, messagePrinted)
        pathToFileInRes = handleGettingFileFromArtifactory(pathToFile, pathToDirRes, fileMatcher, messagePrinted)
    elif os.path.isdir(checkIfSymlinkAndGetRelativePath(PATH)):
        pathToFile = getPathToLatestFileInDir(checkIfSymlinkAndGetRelativePath(PATH), fileMatcher)
        pathToFileInRes = handleGettingFileFromLocalNetwork(pathToFile, pathToDirRes, fileMatcher, messagePrinted)
    else:
        pathToFile = checkIfSymlinkAndGetRelativePath(PATH)
        pathToFileInRes = handleGettingFileFromLocalNetwork(pathToFile, pathToDirRes, fileMatcher, messagePrinted)
    return pathToFileInRes

#-------------------------------------------------------------------------------


#===============================================================================
# functions to get PATHS from ini file
#===============================================================================

def createNewIniFile(pathToFile):
    try:
        f = open(pathToFile, 'w')
        try:
            f.write("\
# You can specify PATH_NAHKA and PATH_STRATIX in this file.\n\
# If you will delete this ini file - a new one will be created.\n\
\n\
\n\
\n\
# 1. Examples of typical paths:\n\
\n\
# 1a. If you will not specify full path to file - script will automatically find the newest file in a given directory:\n\
#     PATH_NAHKA = V:\\some_user\\nahka\\tmp\\deploy\\images\\nahka\n\
#     PATH_STRATIX = R:\\some_user\\stratix10-aaib\\tmp-glibc\\deploy\\images\\stratix10-aaib\n\
\n\
# 1b. Equal sign \"=\" is optional. Count of spaces \" \" before and after path also doesn't matter:\n\
#     PATH_NAHKA ./nahka/tmp/deploy/images/nahka/FRM-rfsw-image-install_20190231120000-multi.tar\n\
#     PATH_STRATIX                   C:\\LocalDir\\rfsw-package-aafia-5mf5_0xFFFFFFFF.tar       #you can also put comments after path (just put a hash sign \"#\" before comment)\n\
\n\
# 1c. If a directory name is just some number (eg. \"1234\") - put \"./\" before its name (eg. \"./1234\") to differentiate it from artifactory URL build number:\n\
#     PATH_NAHKA = LocalDir\n\
#     PATH_STRATIX = ./1234\n\
\n\
\n\
\n\
# 2. Example of how to download newest Nahka file when running this script on Stratix build server:\n\
\n\
# 2a. Please remember to put a colon sign \":\" between server address and a path to directory:\n\
#     PATH_NAHKA = some_user@wrlinb110.emea.nsn-net.net:/var/fpwork/some_user/nahka/tmp/deploy/images/nahka\n\
#     PATH_STRATIX = ./stratix10-aaib/tmp-glibc/deploy/images/stratix10-aaib\n\
\n\
\n\
\n\
# 3. Example of how to download file from artifactory:\n\
\n\
# 3a. You can specify only a Jenkins build number which will automatically use PATH_ARTIFACTORY_TEMPLATE to generate full URL.\n\
#     Count of stars \"*******\" in the template doesn't matter, but at least one star \"*\" must be present to indicate build number position in URL:\n\
#     PATH_ARTIFACTORY_TEMPLATE = https://artifactory-espoo1.int.net.nokia.com/artifactory/mnprf_brft-local/mMIMO_FDD/FB1813_Z/PROD_mMIMO_FDD_FB1813_Z_release/*******/C_Element/SE_RFM/SS_mMIMO_FDD/Target\n\
#     PATH_NAHKA = .\n\
#     PATH_STRATIX = 1234\n\
\n\
# 3b. You can also use just a direct URL to a file:\n\
#     PATH_STRATIX = https://artifactory-espoo1.int.net.nokia.com/artifactory/mnprf_brft-local/mMIMO_FDD/FB1813_Z/PROD_mMIMO_FDD_FB1813_Z_release/1234/C_Element/SE_RFM/SS_mMIMO_FDD/Target/rfsw-package-aafia-5mf5_0xFFFFFFFF.tar\n\
\n\
\n\
\n\
PATH_ARTIFACTORY_TEMPLATE = https://artifactory-espoo1.int.net.nokia.com/artifactory/mnprf_brft-local/mMIMO_FDD/FB1813_Z/PROD_mMIMO_FDD_FB1813_Z_release/*******/C_Element/SE_RFM/SS_mMIMO_FDD/Target\n\
\n\
PATH_NAHKA = .\n\
PATH_STRATIX = .\n\
\n\
")
            f.close()
        except (OSError, IOError) as e:
            print("\nInifile creation ERROR: createNewIniFile(e1) %s - %s" % (e.filename, e.strerror))
        finally:
            f.close()
    except (Exception) as e:
        print("\nInifile creation ERROR: createNewIniFile(e2) %s" % (e))


def loadIniFileIntoList(pathToFile):
    if not os.path.isfile(pathToFile):
        createNewIniFile(pathToFile)
        print("\n%s file has been created!!!\n" % (pathToFile))
        print("You can find detailed information about accepted path formats in there...")
        print("By default script will be searching for Nahka and Stratix files in the current working directory (%s)." % (os.path.dirname(os.path.realpath(sys.argv[0]))))
        pressEnterToContinue()
    try:
        f = open(pathToFile, 'r')
        try:
            linesList = f.readlines()
            f.close()
            return linesList
        except (OSError, IOError) as e:
            print("\nInifile loading ERROR: loadIniFileIntoList(e1) %s - %s" % (e.filename, e.strerror))
            return []
        finally:
            f.close()
    except (Exception) as e:
        print("\nInifile loading ERROR: loadIniFileIntoList(e2) %s" % (e))
        return []


def getPathFromLine(index, commentIndex, line, pathName):
    if commentIndex > 0:
        line = line[index+len(pathName):commentIndex]
    else:
        line = line[index+len(pathName):]
    line = line.lstrip()
    line = line.lstrip('=')
    line = line.strip()
    return line


def getPathsFromIniFile(pathToFileIni):
    PATH_NAHKA = ""
    PATH_STRATIX = ""
    PATH_ARTIFACTORY_TEMPLATE = ""
    pathNahka = 'PATH_NAHKA'
    pathStratix = 'PATH_STRATIX'
    pathArtifactoryTemplate = 'PATH_ARTIFACTORY_TEMPLATE'
    iniFile = loadIniFileIntoList(pathToFileIni)
    if iniFile:
        for line in iniFile:
            commentIndex = line.find('#')
            if commentIndex == 0:
                continue
            index = line.find(pathNahka)
            if index >= 0 and (index < commentIndex or commentIndex < 0):
                PATH_NAHKA = getPathFromLine(index, commentIndex, line, pathNahka)
                continue
            index = line.find(pathStratix)
            if index >= 0 and (index < commentIndex or commentIndex < 0):
                PATH_STRATIX = getPathFromLine(index, commentIndex, line, pathStratix)
                continue
            index = line.find(pathArtifactoryTemplate)
            if index >= 0 and (index < commentIndex or commentIndex < 0):
                PATH_ARTIFACTORY_TEMPLATE = getPathFromLine(index, commentIndex, line, pathArtifactoryTemplate)
    else:
        print("\nInifile loading ERROR: getPathsFromIniFile(e1) Script will now search for Nahka and Stratix files in the current working directory")
        PATH_NAHKA = "."
        PATH_STRATIX = "."
        PATH_ARTIFACTORY_TEMPLATE = "."
    PATHS = {}
    PATHS['PATH_NAHKA'] = PATH_NAHKA
    PATHS['PATH_STRATIX'] = PATH_STRATIX
    PATHS['PATH_ARTIFACTORY_TEMPLATE'] = PATH_ARTIFACTORY_TEMPLATE
    return PATHS


def setNewPathInLine(pathName, PATH_in_ini_file, PATH_new):
    #PATH_matcher = re.compile(r'%s' % (PATH_in_ini_file))
    #PATH_full_matcher = re.compile(r'(.*)(%s)((?!%s).)*?(\s*?=?\s*?)(%s)(.*)' % (pathName, pathName, PATH_in_ini_file))
    if PATH_in_ini_file:
        #return lambda fileContent : PATH_full_matcher.sub((r'\1\2\g<3>%s\5' % (PATH_new)), fileContent)
        return lambda fileContent : fileContent.replace(PATH_in_ini_file, PATH_new)

    return lambda fileContent : fileContent + ('\n%s = %s' % (pathName, PATH_new))


def setNewPathInIniFile(pathToFileIni, pathName, PATH_new):
    PATH_in_ini_file = ""
    iniFile = loadIniFileIntoList(pathToFileIni)
    if iniFile:
        i = -1
        last_occurrence = -1
        for line in iniFile:
            i += 1
            commentIndex = line.find('#')
            if commentIndex == 0:
                continue
            index = line.find(pathName)
            if index >= 0 and (index < commentIndex or commentIndex < 0):
                #PATH_in_ini_file = getPathFromLine(index, commentIndex, line, pathName)
                last_occurrence = i

        if last_occurrence >=0 :
            #iniFile[last_occurrence].replace(PATH_in_ini_file, PATH_new)
            iniFile[last_occurrence] = '%s = %s\n' % (pathName, PATH_new)
        else:
            iniFile.append('\n%s = %s' % (pathName, PATH_new))

        try:
            if PYTHON_MAJOR >= 3:
                f = open(pathToFileIni, 'w', newline = '')
            else:
                f = open(pathToFileIni, 'wb')
            try:
                f.writelines(iniFile)
                f.close()
            except (OSError, IOError) as e:
                print("\nIni file writing ERROR: setNewPathInIniFile(e1) %s - %s" % (e.filename, e.strerror))
            finally:
                f.close()
        except (Exception) as e:
            print("\nIni file writing ERROR: setNewPathInIniFile(e2) %s" % (e))

    else:
        print("\nInifile loading ERROR: setNewPathInIniFile(e1)")



def getUserInput(text):
    userInput = ""
    if PYTHON_MAJOR==2:
        userInput = raw_input(text) #python2 only
    else:
        userInput = input(text) #python3 only
    return userInput.strip()


def askUserToProvideNewPaths(pathToFileIni, PATHS):
    print("path formats allowed:\n\
- local folder (for example: ./1234 - if folder is a numer it must be preceded with \"./\")\n\
- mapped disk drive\n\
- other linux server\n\
- url to artifactory\n\
- just a build number at artifactory (for example: 1234)\n\
- dot means current working directory(for example: .)\n\
if path doesn't contain a filename - script will automatically find the newest file in that folder\n\
(you can find detailed examples in: %s)\n" % pathToFileIni)

    print("\npaths stored in the ini file:")
    print("PATH_NAHKA = %s" % (PATHS.get("PATH_NAHKA", "")))
    print("PATH_STRATIX = %s" % (PATHS.get("PATH_STRATIX", "")))
    print("\nYou can change these paths now. If you don't want to change selected PATH just press Enter...")

    userInput = getUserInput("PATH_NAHKA = ")
    if userInput:
        PATHS['PATH_NAHKA'] = userInput
        setNewPathInIniFile(pathToFileIni, 'PATH_NAHKA', userInput)

    userInput = getUserInput("PATH_STRATIX = ")
    if userInput:
        PATHS['PATH_STRATIX'] = userInput
        setNewPathInIniFile(pathToFileIni, 'PATH_STRATIX', userInput)

#-------------------------------------------------------------------------------


#===============================================================================
# === MAIN FUNCTION ===
#===============================================================================

def main():

#----------------------------
# initial settings of dir and file names used by this script (can be changed to any)
#----------------------------
    pathToFileIni           = r'stratix_nahka_swapper.ini'
    pathToDirResources      = r'stratix_nahka_swapper_resources'
    pathToDirTemp           = r'SRM_temp_00000000'
    pathToDirTempArtifacts  = os.path.join(pathToDirTemp, r'artifacts')


#----------------------------
# initial settings of regex patterns
#----------------------------
    urlMatcher              = re.compile(r'(https://|http://|ftp://)')
    serverMatcher           = re.compile(r'(wrlin)(.*)(emea.nsn-net.net)')
    imageMatcherNahka       = r'*FRM-rfsw-image-install_*'
    imageMatcherStratix     = r'*rfsw-package-aafia-5mf5.0x*'
    fileMatcherNahka        = re.compile(r'(.*)(FRM-rfsw-image-install_)([0-9]{14})(-multi.tar)(.*)')
    fileMatcherStratix      = re.compile(r'(.*)(rfsw-package-aafia-5mf5.0x)([a-fA-F0-9]{8})(.tar)(.*)')
    fileMatcherChecksum     = re.compile(r'(.*0x)([a-fA-F0-9]{1,8})(.*)')
    fileMatcherInstaller    = re.compile(r'.*-installer.sh')


#----------------------------
# get paths from ini file
#----------------------------
    PATHS = getPathsFromIniFile(pathToFileIni)

    askUserToProvideNewPaths(pathToFileIni, PATHS)

    PATH_NAHKA = PATHS.get("PATH_NAHKA", "")
    PATH_STRATIX = PATHS.get("PATH_STRATIX", "")
    PATH_ARTIFACTORY_TEMPLATE = PATHS.get("PATH_ARTIFACTORY_TEMPLATE", "")


#----------------------------
# print Fun Fact!
#----------------------------
    printFunFact()


#----------------------------
# copy files to local resources
#----------------------------
    pathToFileInResourcesNahka = handleGettingFile(pathToDirResources, serverMatcher, urlMatcher, imageMatcherNahka, fileMatcherNahka, PATH_ARTIFACTORY_TEMPLATE, PATH_NAHKA, 'Nahka')
    pathToFileInResourcesStratix = handleGettingFile(pathToDirResources, serverMatcher, urlMatcher, imageMatcherStratix, fileMatcherStratix, PATH_ARTIFACTORY_TEMPLATE, PATH_STRATIX, 'Stratix')


#----------------------------
# swap Nahka file contained within Stratix file
#----------------------------
    extractTarfile(pathToDirTemp, pathToFileInResourcesStratix)
    replaceFileInArtifacts(pathToDirTempArtifacts, pathToFileInResourcesNahka, fileMatcherNahka)
    setNewFileNameInInstallerScripts(pathToDirTemp, pathToFileInResourcesNahka, fileMatcherInstaller, fileMatcherNahka)
    fileNameStratixTemp = fileMatcherStratix.sub(r'\2FFFFFFFF\4', pathToFileInResourcesStratix)
    createTarfile(pathToDirTemp, fileNameStratixTemp)
    removeDir(pathToDirTemp)


#----------------------------
# calculate checksum and rename Stratix file
#----------------------------
    checksum = getChecksum(fileNameStratixTemp)
    fileNameStratixNew = getNewChecksumFileName(fileNameStratixTemp, fileMatcherChecksum, getChecksumAsHex(checksum))
    renameStratixFile(fileNameStratixTemp, fileNameStratixNew)



if __name__ == '__main__':
    main()
    pressEnterToExit()
