"""
Etapa `particion` del pipeline DVC.

Partición estratificada train/test sobre el dataset limpio. La estratificación
conserva la proporción de churn (~26,5 %) en ambos conjuntos. Cualquier
tratamiento de desbalance (SMOTE, class_weight) se aplicará SOLO sobre train
en la etapa de modelado, para no contaminar la evaluación.

Uso:
    python src/data/split_data.py
"""
from pathlib import Path

import pandas as pd
import yaml
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
PARAMS = yaml.safe_load(open(ROOT / "params.yaml", encoding="utf-8"))


def main() -> None:
    p = PARAMS["split"]
    df = pd.read_csv(ROOT / PARAMS["data"]["processed"])
    train, test = train_test_split(
        df, test_size=p["test_size"], stratify=df[PARAMS["target"]],
        random_state=p["random_state"],
    )
    out_train = ROOT / PARAMS["data"]["train"]
    out_test = ROOT / PARAMS["data"]["test"]
    train.to_csv(out_train, index=False)
    test.to_csv(out_test, index=False)
    print(f"train: {train.shape}, churn={train[PARAMS['target']].mean():.3f}")
    print(f"test:  {test.shape}, churn={test[PARAMS['target']].mean():.3f}")


if __name__ == "__main__":
    main()
