import os
import shutil

orginal_dataset_path = "StarGAN/data/ns_part1"
split_dataset_path = "StarGAN/data/RaFD/"

ns_part1 = os.listdir(orginal_dataset_path)

for filename in ns_part1:
	name = filename.split('.')[0]

	if name[-1] == "a":
		shutil.copy(orginal_dataset_path+"/"+filename, split_dataset_path+"normal")
	elif name[-1] == "b":
		shutil.copy(orginal_dataset_path+"/"+filename, split_dataset_path+"smile")
