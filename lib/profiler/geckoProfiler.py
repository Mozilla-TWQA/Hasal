from base import BaseProfiler

import os
from geckoprofiler_controller.control_server import ServerController
from geckoprofiler_controller.control_client import ControllerClient
from ..common.logConfig import get_logger

logger = get_logger(__name__)


class GeckoProfiler(BaseProfiler):

    def start_recording(self):
        if self.browser_type == self.env.DEFAULT_BROWSER_TYPE_FIREFOX:
            # Starting server ...
            logger.info('Starting Web Socket server for controlling Gecko-Profiler Add-on ...')
            self.my_server = ServerController()
            self.my_server.start_server()

    def stop_recording(self, **kwargs):
        if self.browser_type == self.env.DEFAULT_BROWSER_TYPE_FIREFOX:
            # TODO: create saving folder
            saving_path = os.path.join(self.env.DEFAULT_PROFILE_OUTPUT_DIR, self.env.output_name)
            if not os.path.exists(saving_path):
                os.makedirs(saving_path)
            saving_url_filename = os.path.join(saving_path, 'URL.txt')

            # Starting client ...
            logger.info('Starting Python Gecko-Profiler Controller ...')
            my_client = ControllerClient(control_server=self.my_server, save_path=saving_path)
            my_client.connect()

            # Opening profiling page ...
            my_client.open_profiling_page()

            # Getting profiling link ...
            link = my_client.get_profiling_link()
            logger.info('>> Profiling Link: {}'.format(link))
            if link:
                with open(saving_url_filename, 'w') as f:
                    f.write(link)

            # Getting profiling file ...
            filepath = my_client.get_profiling_file()
            logger.info('>> Profiling File: {}'.format(filepath))

            logger.info('Wait for sharing finish ...')
            my_client.wait_profiling_link_sharing_finish()

            # Close server and disconnect
            logger.info('Stopping Web Socket server ...')
            my_client.send_stop_server_command()
            my_client.disconnect()
