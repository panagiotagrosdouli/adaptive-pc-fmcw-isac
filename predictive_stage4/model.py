"""Canonical shared architecture for all four Stage-04 objectives."""
from __future__ import annotations
import torch
from torch import nn

class CommunicationAwareGRU(nn.Module):
    """4-D causal history -> 80-step XY forecast.

    Architecture is intentionally objective-agnostic: objective ablations may
    change only loss terms/weights, never model capacity.
    """
    def __init__(self,input_dim=4,hidden_dim=128,num_layers=2,future_steps=80):
        super().__init__(); self.future_steps=future_steps
        self.gru=nn.GRU(input_dim,hidden_dim,num_layers=num_layers,batch_first=True)
        self.head=nn.Sequential(nn.Linear(hidden_dim,hidden_dim),nn.ReLU(),nn.Linear(hidden_dim,future_steps*2))
    def forward(self,x):
        if x.ndim!=3 or x.shape[-1]!=4: raise ValueError("expected [batch,history,4] canonical input")
        _,h=self.gru(x); return self.head(h[-1]).reshape(x.shape[0],self.future_steps,2)
