"""Source-only partial pooling for sparse turn-demand panels.

Ridge random-effect summaries are regularized descriptions, not independently
identified individual curves or calibrated physiological posteriors.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
import stress_features as S
import front_transfer as F

class PooledRecovery:
    def __init__(self, turns, penalty=10.):
        self.turns=turns
        self.penalty=float(penalty)
    def _residual(self, encoder, events, units):
        return events.eta.to_numpy()-encoder.model.predict(encoder.scale.transform(encoder._unscaled(events,units)))[:,0]
    def fit(self, units):
        self.ids=set(units.nfl_id)
        self.events=self.turns[self.turns.nfl_id.isin(self.ids)].copy().reset_index(drop=True)
        self.encoder=S.StressEncoder(self.turns).fit(units)
        self.events['residual']=np.nan
        # Whole-athlete source crossfits avoid in-sample nuisance residuals for
        # training-player profiles; NFL outcomes are never used here.
        for i,j in KFold(3,shuffle=True,random_state=71533).split(units):
            train=units.iloc[i];held=units.iloc[j]
            ref=S.StressEncoder(self.turns).fit(train)
            mask=self.events.nfl_id.isin(held.nfl_id)
            self.events.loc[mask,'residual']=self._residual(ref,self.events.loc[mask],held)
        self.geometry={};self.noise={}
        for drill in F.DRILLS:
            g=self.events[self.events.drill.eq(drill)]
            x=g[['entry','angle']].to_numpy()
            self.geometry[drill]=(x.mean(0),np.maximum(x.std(0),.1))
            means=g.groupby(['nfl_id','event_id']).residual.mean()
            variance=means.groupby('nfl_id').var().dropna()
            self.noise[drill]=max(float(variance.median()) if len(variance) else .02,.0025)
        return self
    def transform(self, units):
        ev=self.turns[self.turns.nfl_id.isin(units.nfl_id)].copy().reset_index(drop=True)
        ev['residual']=self._residual(self.encoder,ev,units)
        lookup=self.events.set_index(['nfl_id','event_id','drill','center']).residual.sort_index()
        for i,r in ev.iterrows():
            key=(r.nfl_id,r.event_id,r.drill,r.center)
            if r.nfl_id in self.ids:ev.loc[i,'residual']=lookup.loc[key]
        result=units[['nfl_id']].copy().set_index('nfl_id')
        for drill in F.DRILLS:
            sub=ev[ev.drill.eq(drill)]
            mean,scale=self.geometry[drill]
            for player,g in sub.groupby('nfl_id'):
                x=(g[['entry','angle']].to_numpy()-mean)/scale
                phi=np.c_[np.ones(len(g)),x,x[:,0]*x[:,1]]
                # Multiple turns in one attempt do not multiply its total weight.
                counts=g.groupby('event_id').event_id.transform('size').to_numpy()
                w=1/counts/(1+g.eta_width.to_numpy()**2/self.noise[drill])
                gram=phi.T@(w[:,None]*phi)
                coef=np.linalg.solve(gram+self.penalty*np.eye(4),phi.T@(w*g.residual.to_numpy()))
                for k,v in enumerate(coef):result.loc[player,f'pool__{drill}__b{k}']=v
                result.loc[player,f'pool__{drill}__information']=np.trace(gram)
                result.loc[player,f'pool__{drill}__attempts']=g.event_id.nunique()
        return result.reset_index()
