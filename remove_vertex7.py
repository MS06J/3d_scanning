bear_file=open('D:/Download/3DScanning/Projects/Models/bear_original_shrinked.off', 'r')
bear_mesh=bear_file.read().strip().split('\n')
bear_file.close()

del bear_mesh[9]

vertex_num=49998
first_row=bear_mesh[1].split()
first_row[0]=str(vertex_num)
first_row[1]=str(int(first_row[1])-1)
bear_mesh[1]=' '.join(first_row)
row_to_delete=0

for i in range(vertex_num+2,len(bear_mesh)):
    mytemp=bear_mesh[i].split()
    for j in range(1,4):
        the_num=int(mytemp[j])
        if the_num==7:
            row_to_delete=i
        elif the_num>7:
            the_num=the_num-1
            mytemp[j]=str(the_num)
        else:
            pass
    bear_mesh[i]=' '.join(mytemp)

del bear_mesh[row_to_delete]

f=open('D:/Download/3DScanning/Projects/Models/bear_original_shrinked_7removed.off', 'w')
for line in bear_mesh:
    print(line, file=f)
f.close()

