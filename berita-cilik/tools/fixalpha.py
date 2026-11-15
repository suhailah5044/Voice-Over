import numpy as np
from scipy import ndimage as nd
def fix(rgba):
    a=rgba[...,3].astype(np.float32)/255
    b=np.clip((a-0.16)/0.42,0,1)            # partial ear/edge alpha -> solid
    lab,n=nd.label(b>0.05)
    if n>1:
        sizes=nd.sum(np.ones_like(b),lab,range(1,n+1))
        big=np.argmax(sizes)+1
        b[(lab!=big)&(lab>0)]=0                # drop stray specks of room
    rows=np.where(b.max(1)>0.5)[0]
    if len(rows):
        top=max(0,rows[0]-40); band=slice(top, min(top+500, b.shape[0]))
        c=nd.grey_closing(b[band], size=(15,41))   # fill gaps where the ears meet the head
        b[band]=np.maximum(b[band],c)
    b=nd.grey_erosion(b,size=(3,3))           # trim room-coloured fringe
    b=nd.gaussian_filter(b,1.0)
    out=rgba.copy(); out[...,3]=(np.clip(b,0,1)*255).astype(np.uint8)
    return out
