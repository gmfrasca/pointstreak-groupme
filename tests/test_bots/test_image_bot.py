import unittest
from psgroupme.bots.image_bot import ImageBot, IMG_EXTENSIONS
import tests.psgm_mocks as psgm_mocks
from unittest import mock
import tempfile
import os
from psgroupme.bots.image_bot import IMG_EXTENSIONS


class TestImageBot(unittest.TestCase):

    IMG_DATA = 'test'
    IMG_DIR = tempfile.mkdtemp()
    IMG_PATH = os.path.join(IMG_DIR, 'test.jpg')
    
    CFG = {
        'bots': [
            {
                "class_name": "bots.ImageBot", 
                "bot_name": "ImageBot", 
                "bot_id": "0", 
                "bot_url": "/imagebot", 
                "public_url": "http://localhost:5000",
                "img_cfg": {
                    "path": IMG_DIR,
                    "dest": "/img"
                }
            }
        ]
    }

    @mock.patch('psgroupme.bots.base_bot.BotResponseManager', return_value=psgm_mocks.BotResponseManagerMock())
    def setUp(self, mock_brm):
        with open(self.IMG_PATH, 'w') as f:
            f.write(self.IMG_DATA)

        for ext in IMG_EXTENSIONS:
            with open(os.path.join(self.IMG_DIR, f'test{ext}.{ext}'), 'w') as f:
                f.write(self.IMG_DATA)
        self.bot = ImageBot(self.CFG['bots'][0])
        

    def tearDown(self):
        os.remove(self.IMG_PATH)

    @mock.patch('psgroupme.bots.image_bot.ImageBot.respond')
    def test_list_images(self, mock_respond):
        self.bot.list_images()
        expected = 'test testbmp testgif testjpeg testjpg testpng'
        mock_respond.assert_called_once_with(expected)

    @mock.patch('psgroupme.bots.image_bot.ImageBot._respond_image')
    def test_respond_image(self, mock_respond):
        self.bot.respond_image("", self.IMG_PATH)
        mock_respond.assert_called_once_with(self.IMG_PATH)

    @mock.patch('psgroupme.bots.image_bot.ImageBot.respond')
    def test_respond_image_helper(self, mock_respond):
        self.bot._respond_image("test")
        expected_url = 'http://localhost:5000/img/test.jpg'
        mock_respond.assert_called_once_with(expected_url)

    @mock.patch('psgroupme.bots.image_bot.ImageBot.respond')
    def test_respond_image_please_specify(self, mock_respond):
        self.bot.respond_image()
        mock_respond.assert_called_once_with("Please specify an image.")

    def test_list_of_files_in_dir(self):
        files = self.bot._list_of_files_in_dir(self.IMG_DIR)
        self.assertIsInstance(files, list)
        self.assertGreater(len(files), 0)
        self.assertIn('testjpg.jpg', files)
        self.assertIn('testpng.png', files)
        self.assertIn('testgif.gif', files)
        self.assertIn('testbmp.bmp', files)
        self.assertIn('testjpeg.jpeg', files)
        self.assertIn('testjpg.jpg', files)
        self.assertIn('test.jpg', files)

    @mock.patch('psgroupme.bots.image_bot.ImageBot.respond')
    def test_respond_image_not_found(self, mock_respond):
        self.bot._respond_image('test.notfound')
        mock_respond.assert_called_once_with("Image not found")
