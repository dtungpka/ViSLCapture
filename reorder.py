import os



folder_1 = ""
folder_2 = "" #ref

ref1_map = os.path.join(folder_1,'config',"map.txt")
ref2_map = os.path.join(folder_2,'config',"map.txt")

with open(ref1_map, 'r') as f:
    ref1_map = f.readlines()

with open(ref2_map, 'r') as f:
    ref2_map = f.readlines()


#only keep lines from line 56
ref1_map = ref1_map[55:]
ref2_map = ref2_map[55:]


ref1 = {ref1_map.split(" => ")[1] : ref1_map.split(" => ")[0] for ref1_map in ref1_map}
ref2 = {ref2_map.split(" => ")[1] : ref2_map.split(" => ")[0] for ref2_map in ref2_map}

to_chage = [] #(ref1, ref2)

for key in ref1.keys():
    if key in ref2.keys():
        if ref1[key] != ref2[key]:
            to_chage.append((ref1[key], ref2[key]))

print(to_chage)


confirm = input("Do you want to change the files? (y/n): ")

if 'n' in confirm:
    exit()

temp_folders = []
folders_1 = os.listdir(os.path.join(folder_1, 'output'))

for folder in folders_1:
    action = folder.split("P")[0]
    for ref1, ref2 in to_chage:
        if action in ref1:
            old_folder = os.path.join(folder_1, 'output',folder)
            new_folder = old_folder.replace(ref1, ref2)
            if old_folder + '_temp' in temp_folders:
                old_folder = old_folder + '_temp'
                temp_folders.remove(old_folder)
            if os.path.isdir(new_folder):
                temp_folders.append(new_folder + "_temp")
                print(f"renaming {new_folder} to {new_folder}_temp")
                #os.rename(new_folder, new_folder + "_temp")
            print(f"renaming {old_folder} to {new_folder}")
            #os.rename(old_folder, new_folder)
            break

    
