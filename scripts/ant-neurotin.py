from pathlib import Path

import mne
from mne_bids import BIDSPath, write_raw_bids, make_dataset_description

mne.set_log_level('WARNING')


# .fif files
folder = Path('/Users/scheltie/Documents/datasets/iclabel/ANT/raw')
files = [file for file in folder.glob('**/*') if file.suffix == '.fif']

# BIDS
bids_root = Path('/Users/scheltie/Documents/datasets/iclabel/ANT/bids')
bids_path = BIDSPath(root=bids_root, datatype='eeg', task='neurofeedback')

# load and process files
for fname in files:
    raw = mne.io.read_raw_fif(fname, preload=True)
    raw.info['line_freq'] = 50.

    # drop events and AUX
    raw.drop_channels(['TRIGGER', 'AUX7', 'AUX8'])

    # rename wrong channel names
    mapping = {
        "FP1": "Fp1",
        "FPZ": "Fpz",
        "FP2": "Fp2",
        "FZ": "Fz",
        "CZ": "Cz",
        "PZ": "Pz",
        "POZ": "POz",
        "FCZ": "FCz",
        "OZ": "Oz",
        "FPz": "Fpz",
    }
    for key, value in mapping.items():
        try:
            mne.rename_channels(raw.info, {key: value})
        except Exception:
            pass

    # add reference channels and montage
    raw.add_reference_channels(ref_channels='CPz')
    raw.set_montage('standard_1020')

    # add device information
    raw.info['device_info'] = dict()
    raw.info['device_info']['type'] = 'EEG'
    raw.info['device_info']['model'] = 'eego mylab'
    raw.info['device_info']['serial'] = '000479'
    raw.info['device_info']['site'] = \
        'https://www.ant-neuro.com/products/eego_mylab'

    # add experimenter
    raw.info['experimenter'] = 'Mathieu Scheltienne'

    # retrieve subject id
    subject = str(int(fname.name.split('-')[0]))
    # update BIDS path
    bids_path.update(subject=subject)

    # write BIDS
    write_raw_bids(raw, bids_path, format='BrainVision', allow_preload=True,
                   overwrite=True)

# make dataset description
make_dataset_description(
    bids_root, name='ANT', authors='Mathieu Scheltienne', dataset_type='raw',
    overwrite=True)
