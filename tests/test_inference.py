import ast
import json
from pathlib import Path
import sys
import tempfile
import unittest
import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from inference import predict, load_bundle
BINARY = "Binário"

class InferenceTests(unittest.TestCase):
    def test_models_roundtrip_and_schema(self):
        for task, filename in [(BINARY, "amostra_1.csv"), ("Multiclasse", "amostra_4.csv")]:
            frame = pd.read_csv(ROOT / "amostras" / filename)
            X = frame.drop(columns="Tipos de Ataques")
            y = frame["Tipos de Ataques"]
            estimators = [LogisticRegression(max_iter=2000), SVC(probability=True)] if task == BINARY else [RandomForestClassifier(n_estimators=5, random_state=42), KNeighborsClassifier(n_neighbors=3), XGBClassifier(n_estimators=3, max_depth=2, n_jobs=1)]
            for estimator in estimators:
                encoder = LabelEncoder().fit(y) if isinstance(estimator, XGBClassifier) else None
                target = encoder.transform(y) if encoder is not None else y
                # Execute the actual notebook pipeline factory, without running expensive cells.
                notebook = json.loads((ROOT / "notebooks/4-ml-models.ipynb").read_text(encoding="utf-8"))
                tree = ast.parse("".join(notebook["cells"][3]["source"]))
                factory = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "pipeline_model")
                scope = dict(Pipeline=Pipeline, SimpleImputer=SimpleImputer, StandardScaler=StandardScaler)
                exec(compile(ast.Module(body=[factory], type_ignores=[]), "<factory>", "exec"), scope)
                model = scope["pipeline_model"](estimator).fit(X, target)
                entry = dict(pipeline=model, features=list(X), task=task, encoder=encoder)
                result = predict(entry, frame)
                np.testing.assert_allclose(result.iloc[:,:-1].sum(axis=1), 1, atol=1e-6)
                pd.testing.assert_frame_equal(result, predict(entry, frame[frame.columns[::-1]]))
                bad = X.astype(float).copy()
                bad.iloc[0,0] = np.inf
                self.assertEqual(len(predict(entry,bad)),len(frame))
                with self.assertRaises(ValueError): predict(entry,X.drop(columns=X.columns[0]))
                with self.assertRaises(ValueError): predict(entry,X.assign(unexpected=1))
                with self.assertRaises(ValueError): predict(entry,X.iloc[:0])
                if encoder is not None:
                    self.assertEqual(set(result.columns[:-1]),set(y))
                with tempfile.TemporaryDirectory() as directory:
                    path=Path(directory)/"test.pkl"
                    bundle=dict(schema_version=2,models={BINARY:{"test":entry},"Multiclasse":{"test":entry}})
                    joblib.dump(bundle,path)
                    restored=load_bundle(path)["models"][task]["test"]
                    pd.testing.assert_frame_equal(result,predict(restored,frame))
                    joblib.dump({"legacy":model},path)
                    with self.assertRaises(ValueError): load_bundle(path)

    def test_notebook_syntax(self):
        for path in (ROOT/"notebooks").glob("*.ipynb"):
            notebook=json.loads(path.read_text(encoding="utf-8"))
            for cell in notebook["cells"]:
                if cell["cell_type"]=="code":
                    ast.parse("".join(cell["source"]))
                    self.assertEqual(cell["outputs"],[])

    def test_notebook_export_contract(self):
        notebook=json.loads((ROOT/'notebooks/4-ml-models.ipynb').read_text(encoding='utf-8'))
        frame=pd.read_csv(ROOT/'amostras/amostra_1.csv')
        X=frame.drop(columns='Tipos de Ataques')
        y=frame['Tipos de Ataques']
        model=Pipeline([('imputer',SimpleImputer()),('scale',StandardScaler()),('model',LogisticRegression(max_iter=2000))]).fit(X,y)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'models').mkdir()
            scope=dict(ROOT=root,X_train_2017_bin=X,X_train_2017_multi=X,encoders={'2017':LabelEncoder().fit(y)})
            for name in ['reg','svm','rf','knn','xgb']:
                scope['modelo_'+name+'_2017']=model
            exec(compile(''.join(notebook['cells'][119]['source']),'<export>','exec'),scope)
            bundle=load_bundle(root/'models/modelos.pkl')
            self.assertEqual(len(bundle['models'][BINARY]),2)
            self.assertEqual(len(bundle['models']['Multiclasse']),3)

    def test_missing_model_ui(self):
        from unittest.mock import patch
        import inference
        from streamlit.testing.v1 import AppTest
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(inference,"MODEL_PATH",Path(folder)/"missing.pkl"):
                app=AppTest.from_file(str(ROOT/"scripts/app.py")).run(timeout=30)
                self.assertEqual(len(app.exception),0)
                self.assertGreater(len(app.info),0)

if __name__ == "__main__":
    unittest.main()
