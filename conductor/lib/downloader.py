#!/usr/bin/env python

""" Command Line Process to run downloads.
"""

import argparse
import collections
import imp
import json
import os
import multiprocessing
import ntpath
import re
import requests
import sys
import time
import threading
import traceback

try:
    imp.find_module('conductor')
except ImportError, e:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


from conductor.lib import common, api_client, worker
from conductor.setup import logger, CONFIG

CHUNK_SIZE = 1024


class DownloadWorker(worker.ThreadWorker):
    def __init__(self, *args, **kwargs):
        logger.debug('args are %s', args)
        logger.debug('kwargs are %s', kwargs)

        worker.ThreadWorker.__init__(self, *args, **kwargs)
        self.destination = kwargs['destination']
        self.output_path = kwargs.get('output_path')

    def do_work(self, job):
        logger.debug('got file to download:')

        url  = job['url']
        path = job['path']
        md5  = job['md5']
        size = int(job['size'])

        logger.debug('\turl is %s', url)
        logger.debug('\tpath is %s', path)
        logger.debug('\tmd5 is %s', md5)
        logger.debug('\tsize is %s', size)

        if self.output_path:
            logger.debug('using output_path %s', path)
            path = re.sub(self.destination, self.output_path, path)
            logger.debug('set new path to: %s', path)

        if not self.correct_file_present(path, md5):
            logger.debug('downloading file...')
            self.metric_store.increment('bytes_to_download', size)
            common.retry(lambda: self.download_file(url, path))
            logger.debug('file downloaded')
        else:
            logger.debug('file already exists')

    def download_file(self, download_url, path):
        self.mkdir_p(os.path.dirname(path))
        logger.debug('trying to download %s', path)
        request = requests.get(download_url, stream=True)
        with open(path, 'wb') as file_pointer:
            for chunk in request.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    file_pointer.write(chunk)
                    self.metric_store.increment('bytes_downloaded', len(chunk))
        logger.debug('%s successfully downloaded', path)
        return True

    def mkdir_p(self,path):
        if os.path.isdir(path):
            return True
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise
        return True

    def correct_file_present(self, path, md5):
        logger.debug('checking if %s exists and is uptodate at %s', path, md5)
        if not os.path.isfile(path):
            logger.debug('file does not exist')
            return False

        if not md5 == common.get_base64_md5(path):
            logger.debug('md5 does not match')
            return False

        logger.debug('file is uptodate')
        return True

class ReportThread(worker.Reporter):
    def report_status(self, download_id):
        ''' update status of download '''
        post_dic = {
            'download_id': download_id,
            'status': 'downloading',
            'bytes_downloaded': self.metric_store.get('bytes_downloaded'),
            'bytes_to_download': self.metric_store.get('bytes_to_download'),
        }
        response_string, response_code = self.api_helper.make_request('/downloads/status', data=json.dumps(post_dic))
        logger.debug("updated status: %s\n%s", response_code, response_string)
        return response_string, response_code


    def start(self, download_id):
        while self.working and not common.SIGINT_EXIT:
            self.report_status(download_id)
            time.sleep(10)


class Download(object):
    naptime = 15
    def __init__(self, args):
        logger.debug('args are: %s', args)

        self.job_id = args.get('job_id')
        self.task_id = args.get('task_id')
        self.output_path = args.get('output')
        logger.info("output path=%s, job_id=%s, task_id=%s" % \
            (self.output_path, self.job_id, self.task_id))
        self.location = args.get("location") or CONFIG.get("location")
        self.thread_count = CONFIG['thread_count']
        self.api_helper = api_client.ApiClient()
        common.register_sigint_signal_handler()

    def handle_response(self, download_info, job_id=None):
        manager = self.create_manager(download_info, job_id)
        for download in download_info['downloads']:
            manager.add_task(download)
        job_output = manager.join()
        if job_output == True:
            # report success
            logger.debug('job successfully completed')
            return True
        # report failure
        logger.debug('job failed:')
        logger.debug(job_output)
        return False

    def create_manager(self, download_info, job_id):
        args=[]
        kwargs={'thread_count': self.thread_count,
                'output_path': self.output_path,
                'destination': download_info['destination']}
        job_description = [
            (DownloadWorker, args, kwargs)
        ]
        if job_id:
            manager = worker.JobManager(job_description)
        else:
            reporter_description = [(ReportThread, download_info['download_id'])]
            manager = worker.JobManager(job_description, reporter_description)
        manager.start()
        return manager

    def nap(self):
        if not common.SIGINT_EXIT:
            time.sleep(self.naptime)

    def main(self,job_id=None):
        logger.info('starting downloader...')
        if job_id:
            logger.debug('getting download for job %s', job_id)
            self.do_loop(job_id=job_id)
        else:
            logger.debug('running downloader daemon')
            self.loop()

    def loop(self):
        while not common.SIGINT_EXIT:
            try:
                self.do_loop()
            except Exception, e:
                logger.error('hit uncaught exception: \n%s', e)
                logger.error(traceback.format_exc())
            finally:
                self.nap()

    def do_loop(self,job_id=None):
        next_download = self.get_next_download(job_id=job_id)
        if not next_download:
            return
        self.handle_response(next_download, job_id)

    def get_next_download(self, job_id=None, task_id=None):
        logger.debug('in get next download')
        try:
            if job_id:
                endpoint = '/downloads/%s' % job_id
            else:
                endpoint = '/downloads/next'

            logger.debug('endpoint is %s', endpoint)
            if task_id:
                if not job_id:
                    raise ValueError("you need to specify a job_id when passing a task_id")
                params = {'tid': task_id}
            else:
                params = None
            logger.debug('params is: %s', params)

            json_data = json.dumps({'location': self.location})
            logger.debug('json_data is: %s', json_data)
            response_string, response_code = self.api_helper.make_request(endpoint, data=json_data, params=params)
            logger.debug("response code is:\n%s" % response_code)
            logger.debug("response data is:\n%s" % response_string)

            if response_code != 201:
                return None

            download_job = json.loads(response_string)

            return download_job

        except Exception, e:
            logger.error('could not get next download: \n%s', e)
            logger.error(traceback.format_exc())
            return None


def run_downloader(args):
    '''
    Start the downloader process. This process will run indefinitely, polling
    the Conductor cloud app for files that need to be downloaded.
    '''
    # convert the Namespace object to a dictionary
    args_dict = vars(args)
    logger.debug('Downloader parsed_args is %s', args_dict)

    downloader = Download(args_dict)
    downloader.main(job_id=args_dict.get('job_id'))

if __name__ == "__main__":
    exit(1)
    print 'args are %s' % args
    run_downloader(args)
