import scipy.io as sio
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt



def extract_QE_data(file):
    '''
    input: 
    file - a .mat file with QE corr plot data
    output: 
    d - a dictionary with the 3-dimensional QE information
    please note - x and y are arbitrary names, the first dimention is the same as the 
    direction noted in the corr plot title, the second is the orthogonal transverse direction. 
    
    example, if it is a horizontal scan, the "x" direction is the horizontal direction on the cathode.
    '''
    data = sio.loadmat(file)['data'][0][0]
    print(file)

    iterations = len(data[3][0])
    charges = []
    x = []
    y = []
    d = {}
    for i in range(iterations):
        x.append(data[2][0][i][1][0][0])
        y.append(data[2][1][i][1][0][0])
        charges.append(data[3][0][i][0][1][0][0])

    d["x"] = np.array(x)
    d["y"] = np.array(y)
    d["z"] = np.array(charges)
    return d
        
def plot_QE(d):
    '''
    input: 
    d - a dictionary with the 3-dimensional QE information
    output:
    figure plotting a 3-D projection of the QE map
    '''
    fig = plt.figure(figsize = (10,10))
    ax = fig.gca(projection='3d')
    ax.plot_trisurf(d["x"], d["y"], d["z"]/np.max(d["z"]), cmap=plt.cm.viridis, linewidth=0.02)
    ax.view_init(50, 20)
    return fig, ax