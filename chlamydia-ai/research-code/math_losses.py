import torch
import torch.nn.functional as F
EPS=1e-7

def dice_loss(logits,target):
    p=torch.sigmoid(logits); target=target.float()
    d=tuple(range(1,p.ndim)); inter=(p*target).sum(d); den=p.sum(d)+target.sum(d)
    return (1-(2*inter+EPS)/(den+EPS)).mean()

def focal_tversky_loss(logits,target,alpha=.7,beta=.3,gamma=.75):
    p=torch.sigmoid(logits); target=target.float(); d=tuple(range(1,p.ndim))
    tp=(p*target).sum(d); fn=((1-p)*target).sum(d); fp=(p*(1-target)).sum(d)
    t=(tp+EPS)/(tp+alpha*fn+beta*fp+EPS)
    return ((1-t)**gamma).mean()

def boundary_loss(logits,target):
    p=torch.sigmoid(logits); target=target.float()
    kx=torch.tensor([[-1.,0.,1.],[-2.,0.,2.],[-1.,0.,1.]],device=logits.device).view(1,1,3,3); ky=kx.transpose(-1,-2)
    def g(z):
        gx=F.conv2d(z,kx,padding=1); gy=F.conv2d(z,ky,padding=1)
        return torch.sqrt(gx*gx+gy*gy+EPS)
    return F.l1_loss(g(p),g(target))

def brier_loss(logits,target):
    return ((torch.sigmoid(logits)-target.float())**2).mean()

def js_binary(a,b):
    a=a.clamp(EPS,1-EPS); b=b.clamp(EPS,1-EPS); m=.5*(a+b)
    def kl(p,q): return p*torch.log(p/q)+(1-p)*torch.log((1-p)/(1-q))
    return .5*(kl(a,m).mean()+kl(b,m).mean())

def composite_loss(logits,target,paired_prob=None):
    loss=focal_tversky_loss(logits,target)+dice_loss(logits,target)+.2*boundary_loss(logits,target)+.1*brier_loss(logits,target)
    if paired_prob is not None: loss=loss+.25*js_binary(torch.sigmoid(logits),paired_prob)
    return loss
