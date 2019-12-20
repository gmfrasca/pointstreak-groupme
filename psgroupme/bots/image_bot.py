from psgroupme.bots.base_bot import BaseBot
import os

IMG_EXTENSIONS = ['jpg', 'jpeg', 'gif', 'png', 'bmp']


class ImageBot(BaseBot):

    def list_images(self, *args, **kwargs):
        searchdir = self.bot_data.get('img_cfg', dict()).get('path')
        files = self._list_of_files_in_dir(searchdir) if searchdir else []
        self.respond(' '.join(['.'.join(x.split('.')[:-1]) for x in files if
                               x.split('.')[-1] in IMG_EXTENSIONS]))

    def respond_image(self, *args, **kwargs):
        if len(args) > 1:
            self._respond_image(args[1])
        else:
            self.respond("Please specify an image.")

    def _list_of_files_in_dir(self, searchdir, show_all=False):
        files = [x for x in os.listdir(searchdir) if
                 os.path.isfile(os.path.join(searchdir, x))]
        if show_all is False:
            files = [x for x in files if x.startswith("0000") is False]
        return files

    def _respond_image(self, searchfor):
        self._logger.info("Searching {} for image".format(searchfor))
        searchfor = os.path.basename(searchfor)
        public_url = self.bot_data.get('public_url').strip('/')
        img_cfg = self.bot_data.get('img_cfg')
        searchdir = img_cfg.get('path')
        dest = img_cfg.get('dest').strip('/')
        if img_cfg and searchdir and dest:
            # This is for ACL reasons
            found_files = self._list_of_files_in_dir(searchdir, show_all=True)
            for file_type in IMG_EXTENSIONS:
                filename = '{}.{}'.format(searchfor, file_type)
                if filename in found_files:
                    url = '{}/{}/{}'.format(public_url, dest, filename)
                    self._logger.info("Found Image: {}".format(url))
                    self.respond(url)
                    return
