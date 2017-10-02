import pytest

from ..algorithms.segment import trained_model


@pytest.fixture
def dicom_path():
    yield '../images/LIDC-IDRI-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
          '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'


def test_segment_predict(dicom_path):
    predicted = trained_model.predict(dicom_path, [])

    assert predicted['volumes'] == []


def test_classify_predict_inference(dicom_path):
    predicted = trained_model.predict(dicom_path, [{'x': 50, 'y': 50, 'z': 21}])

    assert isinstance(predicted['binary_mask_path'], str)
    assert isinstance(predicted['volumes'], list)
