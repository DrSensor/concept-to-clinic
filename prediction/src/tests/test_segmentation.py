import os
import glob
import pytest
from config import Config

from ..algorithms.segment import trained_model


def test_correct_paths():
    assert os.path.isdir(Config.SEGMENT_ASSETS_DIR)

    for path in glob.glob(Config.DICOM_PATHS_DOCKER_WILDCARD):
        assert os.path.isdir(path)


def test_segment_predict(dicom_path, nodule_locations):
    predicted = trained_model.predict(dicom_path, nodule_locations)
    assert predicted['volumes']
    assert predicted['volumes'][0] > 0


def test_classify_predict_inference(dicom_path, nodule_locations):
    predicted = trained_model.predict(dicom_path, nodule_locations)
    assert isinstance(predicted['binary_mask_path'], str)
    assert isinstance(predicted['volumes'], list)
