from pathlib import Path
import shutil

import mne
from mne_bids import BIDSPath, write_raw_bids, make_dataset_description


mne.set_log_level('WARNING')


# .fif files
folder = Path('/Users/scheltie/Documents/datasets/iclabel/EGI/raw/')
files = [file for file in folder.glob('*/')
         if file.is_dir() or file.suffix == '.mff']

# add .mff extension
for file in files:
    if file.is_file():
        continue
    shutil.move(file, file.with_suffix('.mff'))

# sanity-check
files = [file for file in folder.glob('*/') if file.suffix == '.mff']

# mark bad channels
bads = '31 67 73 82 91 92 102 111 120 133 145 165 174 187 199 208 209 216 217 218 219 225 226 227 228 229 230 231 232 233 234 235 236 237 238 239 240 241 242 243 244 245 246 247 248 249 250 251 252 253 254 255 256'
bads = bads.split(' ')
bads = [f'E{k}' for k in bads]

# BIDS
bids_root = Path('/Users/scheltie/Documents/datasets/iclabel/EGI/bids')
bids_path = BIDSPath(root=bids_root, datatype='eeg', task='restEyesClosed')

for k, fname in enumerate(files):
    raw = mne.io.read_raw_egi(fname, preload=True)
    raw.info['line_freq'] = 50.

    # add experimenter
    raw.info['experimenter'] = 'Vincent Rochas'

    # add bads
    raw.info['bads'] = bads

    # update BIDS path
    bids_path.update(subject=k)

    # write BIDS
    write_raw_bids(raw, bids_path, format='BrainVision', allow_preload=True,
                   overwrite=True)

# make dataset description
make_dataset_description(
    bids_root, name='EGI', authors='Vincent Rochas', dataset_type='raw',
    overwrite=True)
