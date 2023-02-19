import os
import glob
import pandas as pd

actual_directory = os.getcwd()
os.chdir(os.path.join(actual_directory, 'training-sets'))

file_out = 'train-merged.csv'

extension = 'csv'
all_files = list(glob.glob(f'*.{extension}'))
merged = pd.concat([pd.read_csv(f) for f in all_files])
merged.to_csv(file_out, index=False, encoding='utf-8-sig')
