import pandas as pd
from lifelines import KaplanMeierFitter
from sqlalchemy.orm import Session
from backend.database.models import SurvivalDataset

def get_kaplan_meier_curves(db: Session, group_by: str = None):
    records = pd.read_sql(db.query(SurvivalDataset).statement, db.bind)
    if records.empty:
        return []
        
    kmf = KaplanMeierFitter()
    results = []
    
    if group_by and group_by in records.columns:
        groups = records[group_by].unique()
        for group in groups:
            mask = records[group_by] == group
            if mask.sum() > 0:
                kmf.fit(records['duration'][mask], event_observed=records['event'][mask])
                
                timeline = kmf.timeline.tolist()
                survival_prob = kmf.survival_function_.iloc[:, 0].tolist()
                
                results.append({
                    "group": str(group),
                    "timeline": timeline,
                    "survival_probability": survival_prob,
                    "events": int(records['event'][mask].sum()),
                    "censored": int((~records['event'][mask].astype(bool)).sum()),
                    "median_survival": float(kmf.median_survival_time_) if kmf.median_survival_time_ != float('inf') else None
                })
    else:
        kmf.fit(records['duration'], event_observed=records['event'])
        timeline = kmf.timeline.tolist()
        survival_prob = kmf.survival_function_.iloc[:, 0].tolist()
        
        results.append({
            "group": "Overall",
            "timeline": timeline,
            "survival_probability": survival_prob,
            "events": int(records['event'].sum()),
            "censored": int((~records['event'].astype(bool)).sum()),
            "median_survival": float(kmf.median_survival_time_) if kmf.median_survival_time_ != float('inf') else None
        })
        
    return results
