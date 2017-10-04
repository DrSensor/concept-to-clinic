import glob
import os

import numpy as np
import pylidc as pl


def get_dicom_paths(in_docker=True):
    """Return DICOM paths to all LIDC directories depending on whether Docker is used or not
    e.g. ['../images_full/LIDC-IDRI-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
          '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192']

    Args:
        in_docker: whether this method is invoked from within docker or from the prediction directory
    """
    if in_docker:
        return glob.glob(os.path.join('..', 'images_full', 'LIDC-IDRI-*', '**', '**'))
    else:
        return glob.glob(os.path.join('..', 'tests', 'assets', 'test_image_data', 'full', 'LIDC-IDRI-*', '**', '**'))


def prepare_training_data(in_docker=True):
    """Save a boolean mask of each DICOM scan at ../assets/segmented_lung_patient_{LIDC-ID}.npy that indicates whether
    a pixel was annotate by an expert as at least intermediate malicious or not.

    Args:
        in_docker: whether this method is invoked from within docker or from the prediction directory
    """
    INTERMEDIATE_MALICIOUS = 3

    current_dir = os.path.dirname(os.path.realpath(__file__))
    assets_dir = os.path.abspath(os.path.join(current_dir, '..', 'assets'))

    dicom_paths = sorted(get_dicom_paths(in_docker=in_docker))
    for path in dicom_paths:
        directories = path.split('/')
        lidc_id_path_index = 2 if in_docker else 5
        lidc_id = directories[lidc_id_path_index]
        lung_patient_file = os.path.join(assets_dir, "segmented_lung_patient_{}".format(lidc_id))

        if os.path.isfile(lung_patient_file):
            continue

        # Compute and save binary mask with information whether pixel is cancerous
        scan = pl.query(pl.Scan).filter(pl.Scan.patient_id == lidc_id).first()
        if scan is None:
            print("Scan for path '{}' was not found".format(path))
            continue
        vol = scan.to_volume(verbose=False)  # Leading zeros have to be removed from the DICOM file names

        # mask_vol is a boolean, indicator volume for the first annotation of the scan.
        mask_vol = np.zeros(vol.shape, dtype=np.bool)

        # Load DICOM files and obtain z-coords for each slice, so we can index into them.
        dicoms = scan.load_all_dicom_images(verbose=False)
        zs = [float(img.ImagePositionPatient[2]) for img in dicoms]

        cancerous_annotations = pl.query(pl.Annotation).filter(pl.Annotation.malignancy >= INTERMEDIATE_MALICIOUS,
                                                               pl.Annotation.scan_id == scan.id).all()

        for annotation in cancerous_annotations:
            mask, bbox = annotation.get_boolean_mask(return_bbox=True)

            # Obtain indexes of `mask` into `mask_vol`
            i1, i2 = bbox[0].astype(np.int)
            j1, j2 = bbox[1].astype(np.int)

            k1 = zs.index(bbox[2, 0])
            k2 = zs.index(bbox[2, 1])

            # In case the area already was segmented, don't overwrite it but add the annotated segmentation
            annotation_area = np.index_exp[i1:i2 + 1, j1:j2 + 1, k1:k2 + 1]
            mask_vol[annotation_area] = np.logical_or(mask, mask_vol[annotation_area])
        np.save(lung_patient_file, mask_vol)
