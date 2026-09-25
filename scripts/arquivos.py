"""Gera amostras de demonstração a partir de CSV com atributos e rótulos."""
import argparse
from pathlib import Path
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rows", type=int, default=100)
    args = parser.parse_args()
    frame = pd.read_csv(args.input)
    if "Tipos de Ataques" not in frame:
        parser.error("CSV precisa da coluna Tipos de Ataques.")
    if not 1 <= args.rows <= len(frame):
        parser.error("Quantidade de linhas inválida.")
    if args.output.exists():
        parser.error("Destino já existe; escolha outro arquivo.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.sample(n=args.rows, random_state=42).to_csv(args.output, index=False)

if __name__ == "__main__":
    main()
