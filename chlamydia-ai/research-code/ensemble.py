import numpy as np
from scipy.optimize import minimize
EPS=1e-8

class CalibratedTeacherEnsemble:
    def __init__(self, objective="brier"):
        self.objective=objective; self.weights_=None
    @staticmethod
    def softmax(a):
        a=a-np.max(a); e=np.exp(a); return e/e.sum()
    def _loss(self,a,P,y):
        w=self.softmax(a); q=np.tensordot(w,P,axes=(0,0)); q=np.clip(q,EPS,1-EPS)
        if self.objective=="nll": return -np.mean(y*np.log(q)+(1-y)*np.log(1-q))
        return np.mean((q-y)**2)
    def fit(self,teacher_probs,y):
        P=np.asarray(teacher_probs,float); y=np.asarray(y,float).reshape(-1)
        if P.ndim>2: P=P.reshape(P.shape[0],-1)
        r=minimize(self._loss,np.zeros(P.shape[0]),args=(P,y),method="L-BFGS-B")
        self.weights_=self.softmax(r.x); return self
    def predict_proba(self,teacher_probs):
        return np.tensordot(self.weights_,np.asarray(teacher_probs,float),axes=(0,0))

def entropy(p):
    p=np.clip(p,EPS,1-EPS)
    return -(p*np.log(p)+(1-p)*np.log(1-p))
