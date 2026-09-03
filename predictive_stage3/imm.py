"""Two-model IMM-style baseline for causal WOMD forecasting.

The filter mixes a low-process-noise CV model (smooth motion) and a
high-process-noise CV model (maneuvering motion). Model probabilities are
updated from causal position innovation likelihoods only.
"""
from __future__ import annotations
import numpy as np

from predictors import Forecast

DT=0.1


class IMM:
    name="IMM"
    def __init__(self, q=(0.25, 9.0), measurement_var=1.0, transition=((0.97,0.03),(0.08,0.92))):
        self.q=np.asarray(q,float); self.r=float(measurement_var); self.T=np.asarray(transition,float)

    @staticmethod
    def matrices(q,r):
        F=np.array([[1,0,DT,0],[0,1,0,DT],[0,0,1,0],[0,0,0,1]],float)
        H=np.array([[1,0,0,0],[0,1,0,0]],float)
        Q=q*np.diag([DT**4/4,DT**4/4,DT**2,DT**2]); R=r*np.eye(2)
        return F,H,Q,R

    def predict(self,history_xy,steps=80):
        h=np.asarray(history_xy,float)
        xs=np.stack([np.r_[h[0],[0.,0.]],np.r_[h[0],[0.,0.]]]); Ps=np.stack([np.eye(4)*10,np.eye(4)*10])
        mu=np.array([0.8,0.2],float)
        for z in h:
            prior=mu@self.T; mixed_x=[]; mixed_P=[]
            for j in range(2):
                w=mu*self.T[:,j]/max(prior[j],1e-15); xj=np.sum(w[:,None]*xs,axis=0)
                Pj=sum(w[i]*(Ps[i]+np.outer(xs[i]-xj,xs[i]-xj)) for i in range(2))
                mixed_x.append(xj); mixed_P.append(Pj)
            likelihood=np.empty(2); nx=[]; nP=[]
            for j in range(2):
                F,H,Q,R=self.matrices(self.q[j],self.r); x=F@mixed_x[j]; P=F@mixed_P[j]@F.T+Q
                y=z-H@x; S=H@P@H.T+R; inv=np.linalg.inv(S); K=P@H.T@inv
                nx.append(x+K@y); nP.append((np.eye(4)-K@H)@P)
                likelihood[j]=np.exp(-0.5*y@inv@y)/(2*np.pi*np.sqrt(max(np.linalg.det(S),1e-15)))
            xs=np.asarray(nx); Ps=np.asarray(nP); mu=prior*likelihood; mu/=max(mu.sum(),1e-15)
        means=[]; covs=[]
        for _ in range(steps):
            mu=mu@self.T
            for j in range(2):
                F,_,Q,_=self.matrices(self.q[j],self.r); xs[j]=F@xs[j]; Ps[j]=F@Ps[j]@F.T+Q
            mean=np.sum(mu[:,None]*xs[:,:2],axis=0)
            cov=sum(mu[j]*(Ps[j,:2,:2]+np.outer(xs[j,:2]-mean,xs[j,:2]-mean)) for j in range(2))
            means.append(mean); covs.append(cov)
        return Forecast(np.asarray(means),np.asarray(covs))
