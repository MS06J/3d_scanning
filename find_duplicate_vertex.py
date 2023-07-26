import numpy as np

delta=0.000001
counter=0

p_f=open('D:/Download/3DScanning/Projects/Models/pinocchino_skeleton - 複製.txt', 'r')

p_file_content=p_f.read().strip()
p_file_content=p_file_content.split('\n')
p_f.close()

del p_file_content[0]

p_coordinates=np.empty((len(p_file_content),3))

for i in range(len(p_file_content)):
    p_file_content[i]=p_file_content[i].split()
    del p_file_content[i][0]

    p_coordinates[i]=(float(p_file_content[i][1]), float(p_file_content[i][2]), float(p_file_content[i][3]))

    # for j in range(len(p_file_content[i])):
    #     p_file_content[i]=np.array(p_file_content[i])


f=open('D:/Download/3DScanning/Projects/Models/pseudo_mesh_5.off', 'r')
file_content=f.read()
file_content=file_content.split('\n')
f.close()

del file_content[0]

for i in range(0, len(file_content)):
    file_content[i]=file_content[i].split()
    for j in range(len(file_content[i])):
        file_content[i][j]=float(file_content[i][j])
    file_content[i]=np.array(file_content[i])

coordinates=file_content[1:1+int(file_content[0][0])]

f2write=open('D:/Download/3DScanning/Projects/Models/pinocchino_match.txt', 'w')
print(29, file=f2write)

for p_idx in range(len(p_coordinates)):
    for idx in range(len(coordinates)):
        if np.linalg.norm(p_coordinates[p_idx]-coordinates[idx])<=delta:
            print('Found match:', p_idx+2, ':', idx+3)
            print(p_idx, idx, file=f2write)
            counter=counter+1
            break
print(counter)
