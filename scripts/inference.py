"""Contrato de inferência para artefatos gerados após a revisão metodológica."""
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "modelos.pkl"

def load_bundle(path=MODEL_PATH):
    bundle = joblib.load(path)
    if not isinstance(bundle, dict) or bundle.get("schema_version") != 2:
        raise ValueError("Modelo legado incompatível. Reexecute o treinamento corrigido.")
    for task in ("Binário", "Multiclasse"):
        if not bundle.get("models", {}).get(task):
            raise ValueError(f"Artefato sem modelos para {task}.")
    return bundle

def predict(entry, frame):
    features = entry["features"]
    frame = frame.drop(columns=["Tipos de Ataques"], errors="ignore").copy()
    if frame.empty:
        raise ValueError("O CSV não contém registros.")
    if frame.columns.duplicated().any():
        raise ValueError("Há nomes de colunas duplicados.")
    missing = sorted(set(features) - set(frame.columns))
    extra = sorted(set(frame.columns) - set(features))
    if missing or extra:
        raise ValueError(f"Colunas ausentes: {missing}; inesperadas: {extra}")
    frame = frame.loc[:, features].apply(pd.to_numeric, errors="raise")
    frame = frame.replace([np.inf, -np.inf], np.nan)
    model = entry["pipeline"]
    predictions = model.predict(frame)
    classes = model.classes_
    encoder = entry.get("encoder")
    if encoder is not None:
        predictions = encoder.inverse_transform(predictions.astype(int))
        classes = encoder.inverse_transform(classes.astype(int))
    probabilities = model.predict_proba(frame)
    names = [str(c) for c in classes]
    if entry["task"] == "Binário":
        names = [{0: "Benigno", 1: "Malicioso"}[int(c)] for c in classes]
        predictions = [{0: "Benigno", 1: "Malicioso"}[int(c)] for c in predictions]
    result = pd.DataFrame(probabilities, columns=names, index=frame.index)
    result["Previsão"] = predictions
    return result
