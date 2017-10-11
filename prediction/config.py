"""
    prediction.config
    ~~~~~~~~~~~~~~~~~

    Provides the flask config options
"""
import glob
import os


class Config(object):
    PROD_SERVER = os.getenv('PRODUCTION', False)
    DEBUG = False
    SEGMENT_ASSETS_DIR = os.path.abspath(os.path.join(os.getcwd(), 'src', 'algorithms', 'segment', 'assets'))
    DICOM_PATHS_DOCKER = glob.glob(os.path.join('/images_full', 'LIDC-IDRI-*', '**', '**'))
    DICOM_PATHS_LOCAL = glob.glob(
        os.path.join(os.getcwd(), 'src', 'tests', 'assets', 'test_image_data', 'full', 'LIDC-IDRI-*', '**', '**'))


class Production(Config):
    pass


class Development(Config):
    DEBUG = True


class Test(Config):
    DEBUG = True
