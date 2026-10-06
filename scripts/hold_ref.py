import pandas as pd, glob
tot={}
for f in sorted(glob.glob("/freqtrade/user_data/data/binance/futures/*_USDT_USDT-1h-futures.feather")):
    d=pd.read_feather(f); d["date"]=pd.to_datetime(d["date"],unit="s" if d["date"].dtype.kind in "iu" else None)
    w=d[(d["date"]>="2026-04-09")&(d["date"]<"2026-10-06")]
    if len(w)<10: continue
    tot[f.split("/")[-1].replace("-1h-futures.feather","")]=100*(w["close"].iloc[-1]/w["open"].iloc[0]-1)
print({k:round(v,2) for k,v in tot.items()})
print("equal-weight basket %:",round(sum(tot.values())/len(tot),2) if tot else None)
