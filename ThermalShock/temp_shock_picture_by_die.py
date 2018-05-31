import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import csv
import re


def get_list():
    fig = plt.figure(figsize=(20, 20))
    ax = Axes3D(fig)
    colors = ['yellow', 'lime', 'silver', 'slategray', 'aqua', 'sienna', 'lightsteelblue', 'fuchsia', 'pink', 'black', 'purple','orange', 'blue', 'red']
    filenames = ['-20_55', '-10_55', '0_55', '10_55', '55_-20', '55_-10', '55_0', '55_10', '0_0', '10_10', '-10_-10', '-20_-20', '25_25', '55_55']
    # plt.legend(filenames)

    y_list = list(range(0, 74)) * 128
    x_list = []
    for x in range(128):    # 获取横坐标
        x_list.extend([x] * 74)
    z_all = []

    for filename in filenames:
        with open(
                'T:\\home\\kouxinyu\\TempShock_ErrorInfo\\temp_shock_{0}_.csv'.
                format(filename)) as csv_file:
            lines = csv.reader(csv_file)
            z_list = [] # 针对每张csv表格清空z_list
            
            for line_obj in lines:
                z_line = [] # 针对每行清空z_line
                line = [x for x in list(line_obj) if x]

                if len(line) > 1:
                    for cell in line[1:]:
                        y_z_drop = re.split('_', cell)
                        z = int(y_z_drop[1])
                        if z > 30000:
                            z = 30000
                        z_line.append(z)
                else:
                    z_line.extend([0] * 74)
                z_list.extend(z_line)
        print(len(z_list))
        z_all.append(z_list)
           
    for z in z_all:
        ax.scatter(x_list, y_list, z, c=colors.pop(), s=10, alpha=1.0)

    ax.legend(filenames)
    ax.set_xlabel('Die Number')
    ax.set_ylabel('Err Bit')
    ax.set_zlabel('Frame Count')            

    # ax.set_xticks(xlist)
    # ax.set_xticklabels(x_ticks_labels, rotation=90)
            

    plt.show()


get_list()