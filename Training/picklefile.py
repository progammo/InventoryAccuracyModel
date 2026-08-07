import pickle

with open("Training\\model.pkl", "rb") as f:
    lgbm = pickle.load(f)

print(lgbm)