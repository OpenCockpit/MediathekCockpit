# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


import os
import re
import threading
from urllib.parse import urljoin
from twisted.internet import reactor
from Components.Task import Task, ReturncodePostcondition
from .WebRequestsAsync import WebRequestsAsync
from .WebRequests import WebRequests
from .Debug import logger
from .ParserMetaFile import ParserMetaFile
from .FileUtils import writeFile, deleteFiles, touchFile
try:
    from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager
except Exception:
    logger.error("CacheCockpit import error")
    FileManager = None


def loadDatabaseFile(target_path, event_name, short_description, description, rec_time, service_ref, length):
    logger.info("target_path: %s, event_name: %s, short_description: %s, service_ref: %s, length: %s",
                target_path, event_name, short_description, service_ref, length)
    file_name = os.path.splitext(target_path)[0]
    writeFile(file_name + ".txt", description)
    ParserMetaFile(target_path).updateMeta(
        {
            "service_reference": service_ref,
            "name": event_name,
            "description": short_description,
            "rec_time": rec_time,
            "length": length
        }
    )
    if FileManager:
        FileManager.getInstance("MVC").loadDatabaseFile(target_path)


def deleteFile(target_path):
    # A permanent, direct delete - these are disposable playback cache files,
    # not user recordings, so MovieCockpit's shared trashcan/bookmark/job-queue
    # machinery (which FileManager.execFileOp(FILE_OP_DELETE, ...) goes through)
    # doesn't apply here and unnecessarily depends on MovieCockpit being installed.
    logger.info("target_path: %s", target_path)
    deleteFiles(os.path.splitext(target_path)[0] + ".*")
    if FileManager:
        # the file may have been added to MovieCockpit's cache while it was still being written
        file_manager = FileManager.getInstance("MVC")
        file_manager.delete("table1", target_path)
        file_manager.delete("table2", os.path.basename(target_path))


class PartPostcondition(ReturncodePostcondition):
    """The postcondition of a task that makes a part of a recording (see MuxTask): it fails if the task fails, so the
    tasks after it are not run. An aborted task does not fail: the user ended it (left the player, aborted the job) and
    gets no error for it; endJob() keeps the tasks after it from being run."""

    def check(self, task):
        return getattr(task, "_aborted", False) or ReturncodePostcondition.check(self, task)


def endJob(task):
    """An aborted task of a job ends it: the tasks after it (the other part, the MuxTask) are dropped, so the job ends
    with it instead of going on with them."""
    job = task.job
    if job is not None and task in job.tasks:
        del job.tasks[job.tasks.index(task) + 1:]


def downloadCover(url, path):
    if url:
        web_request = WebRequests()
        content = web_request.getContent(url)
        data = content if isinstance(content, str) else content.decode("utf-8", errors="replace")
        url = re.findall(r'src":"([^"]+)', data, re.DOTALL)
        if not url:
            url = re.findall(r'image" content="([^"]+)', data, re.DOTALL)
        if url:
            url = url[0]
            url = url.replace("{width}", "1080")
            if "kika.de" in url or "arte.tv" in url:
                url = url.split("?")[0]
                if "arte.tv" in url:
                    url = url + ".jpg"
            web_request.downloadFile(url, path)


class DownloadTaskFile(Task):

    TASK_NAME = "download task"

    def __init__(self, job, url, target_path, event_name, short_description, description, rec_time, service_ref, length, web_site_url, final=True):
        """final: target_path is the recording (it gets its cover and its meta data); else a part of it that a MuxTask
        makes the recording of (the job's target_path), which is deleted with all its parts if this task fails."""
        logger.info("job: %s, url: %s, target_path: %s, description: %s",
                    job, url, target_path, description)
        self.url = url
        self.target_path = target_path
        self.final = final
        self.cleanup_path = target_path if final else job.target_path
        self.event_name = event_name
        self.short_description = short_description
        self.description = description
        self.rec_time = rec_time
        self.service_ref = service_ref
        self.web_site_url = web_site_url
        self.length = length
        self.download = WebRequestsAsync()
        self.totalbytes = 0
        self.recvbytes = 0
        self._aborted = False
        self._failed = False
        self.web_client = None
        Task.__init__(self, job, self.TASK_NAME)
        if not self.final:
            # a part that fails ends the job: the tasks after it (the other part, the MuxTask) are not run
            self.postconditions.append(PartPostcondition())

    def abort(self, *_args):
        logger.info("...")
        self._aborted = True
        endJob(self)
        if self.web_client:
            self.web_client.cancel()
        deleteFile(self.cleanup_path)
        Task.processFinished(self, 1)

    def run(self, callback):
        logger.info("...")
        self.callback = callback
        touchFile(self.target_path)

        if self.final:
            # Prepare cover and metadata in background to avoid blocking the main thread
            threading.Thread(target=self._prepareCoverAndMeta, daemon=True).start()

        self.web_client = self.download.downloadFileAsync(
            url=self.url,
            path=self.target_path
        )

        # Add progress, completion and error callbacks
        self.web_client.addProgback(self.http_progress)
        self.web_client.addCallback(self.http_finished)
        self.web_client.addErrback(self.http_failed)

        # Start the download
        self.web_client.start()

    def _prepareCoverAndMeta(self):
        try:
            downloadCover(self.web_site_url, os.path.splitext(self.target_path)[0] + ".jpg")
            if not self._failed and not self._aborted:
                reactor.callFromThread(
                    loadDatabaseFile, self.target_path, self.event_name, self.short_description,
                    self.description, self.rec_time, self.service_ref, self.length)
        except Exception as e:
            logger.error("Error preparing cover/meta: %s", e)

    def http_progress(self, recvbytes, totalbytes, progress):
        # logger.info("...")
        self.progress = int(self.end * progress / 100)
        self.recvbytes, self.totalbytes = recvbytes, totalbytes

    def http_finished(self, _result):
        # logger.info("result: %s", _result)
        reactor.callFromThread(self._on_finished)

    def _on_finished(self):
        if self._aborted:
            return
        if self.final:
            loadDatabaseFile(self.target_path, self.event_name, self.short_description,
                             self.description, self.rec_time, self.service_ref, self.length)
        Task.processFinished(self, 0)

    def http_failed(self, error_message=""):
        logger.info("...")
        reactor.callFromThread(self._on_failed, error_message)

    def _on_failed(self, error_message=""):
        if self._aborted:
            return
        self._failed = True
        logger.error("error_message: %s", error_message)
        deleteFile(self.cleanup_path)
        Task.processFinished(self, 1)


class DownloadTaskHLS(Task):
    totalbytes = recvbytes = 0

    def __init__(self, job, url, segments, target_path, event_name, short_description, description, rec_time, service_ref, length, web_site_url, final=True):
        """final: see DownloadTaskFile."""
        logger.info("job: %s, url: %s, target_path: %s, description: %s",
                    job, url, target_path, description)
        self.url = url
        self.segments = list(segments)
        self.target_path = target_path
        self.final = final
        self.cleanup_path = target_path if final else job.target_path
        self.event_name = event_name
        self.short_description = short_description
        self.description = description
        self.web_site_url = web_site_url
        self.rec_time = rec_time
        self.service_ref = service_ref
        self.length = length
        self.content = WebRequestsAsync()
        Task.__init__(self, job, "download task")
        if not self.final:
            # a part that fails ends the job: the tasks after it (the other part, the MuxTask) are not run
            self.postconditions.append(PartPostcondition())
        self.totalbytes = len(segments)
        self.file_handle = None
        self._aborted = False
        self._failed = False
        self.web_client = None

    def abort(self, *_args):
        logger.info("...")
        self._aborted = True
        endJob(self)
        self.segments = []
        if self.web_client:
            self.web_client.cancel()
        if self.file_handle and not self.file_handle.closed:
            self.file_handle.close()
        deleteFile(self.cleanup_path)
        Task.processFinished(self, 1)

    def run(self, callback):
        logger.info("...")
        self.callback = callback
        touchFile(self.target_path)

        if self.final:
            # Prepare cover and metadata in background to avoid blocking the main thread
            threading.Thread(target=self._prepareCoverAndMeta, daemon=True).start()

        self.file_handle = open(self.target_path, "wb")  # pylint: disable=consider-using-with
        self.downloadSegment(
            str(urljoin(self.url, self.segments.pop(0).url)))

    def _prepareCoverAndMeta(self):
        try:
            downloadCover(self.web_site_url, os.path.splitext(self.target_path)[0] + ".jpg")
            if not self._failed and not self._aborted:
                reactor.callFromThread(
                    loadDatabaseFile, self.target_path, self.event_name, self.short_description,
                    self.description, self.rec_time, self.service_ref, self.length)
        except Exception as e:
            logger.error("Error preparing cover/meta: %s", e)

    def downloadSegment(self, url):
        logger.info("url: %s", url)
        self.web_client = self.content.getContentAsync(url)
        self.web_client.addCallback(
            self._http_finished_thread).addErrback(self._http_failed_thread)
        self.web_client.start()

    def _http_finished_thread(self, result):
        reactor.callFromThread(self.http_finished, result)

    def http_finished(self, result):
        if self._aborted:
            return
        # logger.info("...")
        # logger.debug("segments: %s", self.segments)
        if result:
            content = result[1] if isinstance(result, tuple) else result
            self.file_handle.write(content)
        else:
            logger.error("Empty segment content received, aborting HLS download")
            if self.file_handle and not self.file_handle.closed:
                self.file_handle.close()
            self._failed = True
            deleteFile(self.cleanup_path)
            Task.processFinished(self, 1)
            return
        self.recvbytes += 1
        self.progress = int(
            round(self.end * self.recvbytes / float(self.totalbytes)))
        if self.segments:
            segment = self.segments.pop(0)
            logger.debug("segment: %s", segment)
            self.downloadSegment(str(urljoin(self.url, segment.url)))
        else:
            self.file_handle.close()
            if self.final:
                loadDatabaseFile(self.target_path, self.event_name, self.short_description,
                                 self.description, self.rec_time, self.service_ref, self.length)
            Task.processFinished(self, 0)

    def _http_failed_thread(self, error):
        reactor.callFromThread(self.http_failed, error)

    def http_failed(self, error):
        if self._aborted:
            return
        logger.info("...")
        if self.file_handle and not self.file_handle.closed:
            self.file_handle.close()

        # Handle both string errors and exception objects
        error_message = str(error) if error else ""
        logger.error("error_message: %s", error_message)
        self._failed = True
        deleteFile(self.cleanup_path)
        Task.processFinished(self, 1)


class MuxTask(Task):
    """Muxes the parts of a recording (the video and the audio track of an HLS stream, downloaded by the tasks before it)
    into the recording, with ffmpeg, without encoding anything. The parts are deleted afterwards; if it fails, the
    recording and its parts are."""

    def __init__(self, job, parts, target_path, event_name, short_description, description, rec_time, service_ref, length, web_site_url):
        logger.info("job: %s, parts: %s, target_path: %s", job, parts, target_path)
        Task.__init__(self, job, "mux task")
        self.parts = parts
        self.target_path = target_path
        self.event_name = event_name
        self.short_description = short_description
        self.description = description
        self.rec_time = rec_time
        self.service_ref = service_ref
        self.length = length
        self.web_site_url = web_site_url
        self.totalbytes = self.recvbytes = 0
        self.weighting = 5   # the copy takes little time compared to the downloads
        self._aborted = False
        self.setTool("ffmpeg")
        self.postconditions = [PartPostcondition()]   # instead of setTool's ReturncodePostcondition: no error when aborted
        self.args += ["-y", "-nostdin", "-loglevel", "error"]
        for part in parts:
            self.args += ["-i", part]
        # the video of the first part, the audio of the others
        self.args += ["-map", "0:v:0"]
        for i in range(1, len(parts)):
            self.args += ["-map", "%d:a:0" % i]
        self.args += ["-c", "copy", "-f", "mp4", target_path]

    def abort(self):
        """Ended by the user: ffmpeg is killed, which finishes the task (without an error, see PartPostcondition); the
        recording and its parts are deleted."""
        logger.info("...")
        self._aborted = True
        if self.container:
            self.container.kill()
        else:
            self.finish()

    def cleanup(self, failed):
        logger.info("failed: %s, aborted: %s", failed, self._aborted)
        for part in self.parts:
            try:
                os.remove(part)
            except OSError:
                pass
        if failed or self._aborted:
            deleteFile(self.target_path)
            return
        loadDatabaseFile(self.target_path, self.event_name, self.short_description,
                         self.description, self.rec_time, self.service_ref, self.length)
        threading.Thread(target=self._prepareCoverAndMeta, daemon=True).start()

    def _prepareCoverAndMeta(self):
        try:
            downloadCover(self.web_site_url, os.path.splitext(self.target_path)[0] + ".jpg")
            reactor.callFromThread(
                loadDatabaseFile, self.target_path, self.event_name, self.short_description,
                self.description, self.rec_time, self.service_ref, self.length)
        except Exception as e:
            logger.error("Error preparing cover/meta: %s", e)
