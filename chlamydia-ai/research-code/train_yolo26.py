import argparse
from ultralytics import YOLO

p=argparse.ArgumentParser()
p.add_argument("--data",required=True)
p.add_argument("--epochs",type=int,default=150)
p.add_argument("--imgsz",type=int,default=1024)
p.add_argument("--device",default=None)
a=p.parse_args()

model=YOLO("yolo26n-seg.pt")
model.train(data=a.data,epochs=a.epochs,imgsz=a.imgsz,device=a.device,
            project="runs/chlamydia",name="yolo26n_seg_student")
