# ---------------------------------------------------------------------------
# MTDA Client
# ---------------------------------------------------------------------------
#
# This software is a part of MTDA.
# Copyright (C) 2021 Siemens Digital Industries Software
#
# ---------------------------------------------------------------------------
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------

import fcntl
import os
import Pyro4
import random
import socket
import subprocess
import tempfile
import time
import zmq
import zstandard as zstd

from mtda.main import MultiTenantDeviceAccess
import mtda.constants as CONSTS


class Client:

    _lockfile = "/tmp/storage_lock"
    def __init__(self, host=None, session=None, config_files=None,
                 timeout=CONSTS.RPC.TIMEOUT):
        """
        Client to control mtda device
        :param host:    hostname or ip of mtda device
        :param session: mtda session id
        :param config_files: configuration filenames
        :param timeout: RPC timeout in seconds
        """
        agent = MultiTenantDeviceAccess()
        agent.load_config(host, config_files=config_files)
        if agent.remote is not None:
            uri = f"PYRO:mtda.main@{agent.remote}:{agent.ctrlport}"
            Pyro4.config.SERIALIZER = "marshal"
            self._impl = Pyro4.Proxy(uri)
            self._impl._pyroTimeout = timeout
        else:
            self._impl = agent
        self._agent = agent
        self._data = None

        if session is None:
            HOST = socket.gethostname()
            USER = os.getenv("USER")
            WORDS = "/usr/share/dict/words"
            if os.path.exists(WORDS):
                WORDS = open(WORDS).read().splitlines()
                name = random.choice(WORDS)
                if name.endswith("'s"):
                    name = name.replace("'s", "")
            elif USER is not None and HOST is not None:
                name = f"{USER}@{HOST}"
            else:
                name = "mtda"
            self._session = os.getenv('MTDA_SESSION', name)
        else:
            self._session = session

    def __getattr__(self, name):
        if self._impl is None:
            return None

        attr = getattr(self._impl, name)
        if self._session and callable(attr):
            def wrapper(*args, **kwargs):
                kwargs['session'] = self._session
                return attr(*args, **kwargs)
            return wrapper
        return attr

    def console_prefix_key(self):
        return self._agent.console_prefix_key()

    def console_getkey(self):
        return self._agent.console_getkey()

    def console_init(self):
        return self._agent.console_init()

    def console_remote(self, host, screen):
        return self._agent.console_remote(host, screen)

    def console_toggle(self):
        return self._agent.console_toggle(self._session)

    def monitor_remote(self, host, screen):
        return self._agent.monitor_remote(host, screen)

    def pastebin_api_key(self):
        return self._agent.pastebin_api_key()

    def pastebin_endpoint(self):
        return self._agent.pastebin_endpoint()

    def _acquire_lock(self):
        self._lock_fd = open(self._lockfile, "w")
        fcntl.flock(self._lock_fd, fcntl.LOCK_EX)

    def _release_lock(self):
        fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
        self._lock_fd.close()

    def storage_network(self, remote):
        self._acquire_lock()
        try:
            cmd_nbd = '/usr/sbin/nbd-client'
            if os.path.exists(cmd_nbd) is False:
                raise RuntimeError(f'{cmd_nbd} not found')

            rdev = self._impl.storage_network()
            if rdev is None:
                raise RuntimeError('could not put storage on network')

            cmd = ['sudo', '/usr/sbin/modprobe', 'nbd']
            subprocess.check_call(cmd)

            cmd = ['sudo', cmd_nbd, '-N', 'mtda-storage', remote]
            subprocess.check_call(cmd)
        finally:
            self._release_lock()

    def storage_open(self):
        tries = 60
        while tries > 0:
            tries = tries - 1
            try:
                host = self.remote()
                port = self._impl.storage_open(self._session)
                context = zmq.Context()
                socket = context.socket(zmq.PUSH)
                hwm = int(CONSTS.WRITER.HIGH_WATER_MARK / CONSTS.WRITER.READ_SIZE)
                socket.setsockopt(zmq.SNDHWM, hwm)
                socket.connect(f'tcp://{host}:{port}')
                self._data = socket
                return
            except Exception:
                if tries > 0:
                    time.sleep(1)
                    pass
                else:
                    raise

    def storage_update(self, dest, src=None, callback=None):
        path = dest if src is None else src
        try:
            st = os.stat(path)
            image_size = st.st_size
        except FileNotFoundError:
            return False

        status = self._impl.storage_update(dest, 0, self._session)
        if status is False:
            return False
        blksz = self._agent.blksz
        impl = self._impl
        session = self._session

        # Get file handler from specified path
        file = ImageFile.new(path, impl, session, blksz, callback)

        # Open the shared storage device so we own it
        self.storage_open()

        try:
            # Prepare for download/copy
            file.prepare(image_size, CONSTS.IMAGE.RAW.value)

            # Copy image to shared storage
            file.copy()

            # Wait for background writes to complete
            file.flush()

        except Exception:
            return False
        finally:
            # Storage may be closed now
            self.storage_close()
        return True

    def storage_write_image(self, path, callback=None):
        self._acquire_lock()
        try:
            blksz = self._agent.blksz
            impl = self._impl
            session = self._session

            # Get file handler from specified path
            file = ImageFile.new(path, impl, session, blksz, callback)

            # Open the shared storage device so we own it
            # It also prevents us from loading a new bmap file while
            # another transfer may be on-going
            self.storage_open()

            # Automatically discover the bmap file
            bmap = None
            image_path = file.path()
            image_size = None
            while True:
                bmap_path = image_path + '.bmap'
                try:
                    bmap = file.bmap(bmap_path)
                    if bmap is not None:
                        import xml.etree.ElementTree as ET

                        bmap = ET.fromstring(bmap)
                        print(f"Discovered bmap file '{bmap_path}'")
                        bmapDict = self.parseBmap(bmap, bmap_path)
                        self._impl.storage_bmap_dict(bmapDict, self._session)
                        image_size = bmapDict['ImageSize']
                        break
                except Exception:
                    pass
                image_path, ext = os.path.splitext(image_path)
                if ext == "":
                    print("No bmap file found at location of image")
                    break

            try:
                # Prepare for download/copy
                file.prepare(self._data, image_size)

                # Copy image to shared storage
                file.copy()

                # Wait for background writes to complete
                file.flush()

            except Exception:
                raise
            finally:
                # Storage may be closed now
                self.storage_close()
                self._impl.storage_bmap_dict(None, self._session)
        finally:
            self._release_lock()

    def parseBmap(self, bmap, bmap_path):
        try:
            bmapDict = {}
            bmapDict["BlockSize"] = int(
                bmap.find("BlockSize").text.strip())
            bmapDict["BlocksCount"] = int(
                bmap.find("BlocksCount").text.strip())
            bmapDict["MappedBlocksCount"] = int(
                bmap.find("MappedBlocksCount").text.strip())
            bmapDict["ImageSize"] = int(
                bmap.find("ImageSize").text.strip())
            bmapDict["ChecksumType"] = \
                bmap.find("ChecksumType").text.strip()
            bmapDict["BmapFileChecksum"] = \
                bmap.find("BmapFileChecksum").text.strip()
            bmapDict["BlockMap"] = []
            for child in bmap.find("BlockMap").findall("Range"):
                range = child.text.strip().split("-")
                first = range[0]
                last = range[0] if len(range) == 1 else range[1]
                bmapDict["BlockMap"].append({
                    "first": int(first),
                    "last": int(last),
                    "chksum": child.attrib["chksum"]
                })
        except Exception:
            print(f"Error parsing '{bmap_path}', probably not a bmap 2.0 file")
            return None
        return bmapDict

    def start(self):
        return self._agent.start()

    def stop(self):
        if self._agent.remote is not None:
            self._impl.close()
        else:
            self._agent.stop()

    def remote(self):
        return self._agent.remote

    def session(self):
        return self._session

    def target_lock(self, retries=0):
        status = False
        while status is False:
            status = self._impl.target_lock(self._session)
            if retries <= 0 or status is True:
                break
            retries = retries - 1
            time.sleep(60)
        return status

    def version(self):
        return self._agent.version

    def video_url(self, host="", opts=None):
        if host == "":
            host = os.getenv("MTDA_REMOTE", "")
        return self._impl.video_url(host, opts)


class ImageFile:
    """ Base class for image files (local or remote) """

    def new(path, agent, session, blksz, callback=None):
        if path.startswith('s3:'):
            return ImageS3(path, agent, session, blksz, callback)
        else:
            return ImageLocal(path, agent, session, blksz, callback)

    def __init__(self, path, agent, session, blksz, callback=None):
        self._agent = agent
        self._blksz = blksz
        self._callback = callback
        self._imgname = os.path.basename(path)
        self._inputsize = 0
        self._path = path
        self._session = session
        self._totalread = 0
        self._totalsent = 0

    def bmap(self, path):
        return None

    def compression(self):
        path = self._path
        if path.endswith(".bz2"):
            result = CONSTS.IMAGE.BZ2.value
        elif path.endswith(".gz"):
            result = CONSTS.IMAGE.GZ.value
        elif path.endswith(".zst"):
            result = CONSTS.IMAGE.ZST.value
        elif path.endswith(".xz"):
            result = CONSTS.IMAGE.XZ.value
        else:
            result = CONSTS.IMAGE.RAW.value
        return result

    def flush(self):
        # Wait for background writes to complete
        agent = self._agent
        callback = self._callback
        imgname = self._imgname
        inputsize = self._inputsize
        totalread = self._totalread
        outputsize = self._outputsize

        agent.storage_flush(self._totalsent)
        while True:
            status, writing, written = agent.storage_status()
            if callback is not None:
                callback(imgname, totalread, inputsize, written, outputsize)
            if writing is False:
                break
            time.sleep(0.5)
        self._socket.close()

    def path(self):
        return self._path

    def prepare(self, socket, output_size=None, compression=None):
        compr = self.compression() if compression is None else compression
        self._inputsize = self.size()
        self._outputsize = output_size
        self._socket = socket
        # if image is uncompressed, we compress on the fly
        if compr == CONSTS.IMAGE.RAW.value:
            compr = CONSTS.IMAGE.ZST.value
        self._agent.storage_compression(compr, self._session)
        self._lastreport = time.time()
        self._totalread = 0

    def progress(self):
        # Report progress via callback
        callback = self._callback
        imgname = self._imgname
        inputsize = self._inputsize
        totalread = self._totalread
        outputsize = self._outputsize
        if callback is not None and time.time() - self._lastreport >= 1:
            _, _, written = self._agent.storage_status(self._session)
            callback(imgname, totalread, inputsize, written, outputsize)
            self._lastreport = time.time()

    def size(self):
        return None

    def _write_to_storage(self, data):
        self._socket.send(data)
        self._totalsent += len(data)


class ImageLocal(ImageFile):
    """ An image from the local file-system to be copied over to the shared
        storage. """

    def __init__(self, path, agent, session, blksz, callback=None):
        super().__init__(path, agent, session, blksz, callback)

    def bmap(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                return f.read()
        return None

    def copy(self):
        if os.path.exists(self._path) is False:
            raise IOError(f'{self._path}: image not found!')

        image = open(self._path, 'rb')
        comp_on_the_fly = False
        if self.compression() == CONSTS.IMAGE.RAW.value:
            cctx = zstd.ZstdCompressor(level=1)
            comp_on_the_fly = True
            inputstream = cctx.stream_reader(image)
        else:
            inputstream = image

        try:
            while (data := inputstream.read(self._blksz)):
                self._totalread = image.tell()
                self.progress()
                self._write_to_storage(data)

        finally:
            if comp_on_the_fly:
                inputstream.close()
            else:
                image.close()

    def size(self):
        st = os.stat(self._path)
        return st.st_size


class ImageS3(ImageFile):
    """ An image to be downloaded from a S3 bucket """

    def __init__(self, path, agent, session, blksz, callback=None):
        super().__init__(path, agent, session, blksz, callback)
        self._object = None

        from urllib.parse import urlparse
        url = urlparse(self._path)
        self._bucket = url.hostname
        self._key = url.path[1:]

    def bmap(self, path):
        from urllib.parse import urlparse

        url = urlparse(path)
        bucket = url.hostname
        key = url.path[1:]
        result = None

        if bucket != self._bucket:
            raise RuntimeError('bmap shall be downloaded from the same S3 '
                               'bucket as the image!')

        bmap = self._open(key)
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
            from boto3.s3.transfer import TransferConfig

            config = TransferConfig(use_threads=False)
            bmap.download_file(Filename=tmp.name, Config=config)
            bmap = None

            tmp.close()
            with open(tmp.name, 'r') as f:
                result = f.read()
            os.unlink(tmp.name)

        return result

    def copy(self):
        if self._object is None:
            self._object = self._open()

        from boto3.s3.transfer import TransferConfig
        config = TransferConfig(use_threads=False)
        self._object.download_fileobj(self, Config=config)

    def size(self):
        if self._object is None:
            self._object = self._open()

        result = None
        if self._object is not None:
            result = self._object.content_length
        return result

    def write(self, data):
        """ called by boto3 as data gets downloaded from S3 """

        dataread = len(data)
        self._totalread += dataread

        # Write block to shared storage device
        self.progress()
        self._write_to_storage(data)

        return dataread

    def _open(self, key=None):
        if key is None:
            key = self._key

        import boto3
        s3 = boto3.resource('s3')
        return s3.Object(self._bucket, key)
