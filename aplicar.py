"""Script para aplicar a tradução fan-made no jogo."""

import csv
import sys
from pathlib import Path

DIR = Path(__file__).parent


def _set_defaults(file: Path):
    """Preenche todas as colunas de tradução fan-made com a tradução oficial brasileira.

    Caso essa função não seja utilizada, os campos vazios terão fallback para a tradução
    oficial inglesa.

    Args:
        file: Arquivo que será modificado.
    """
    with file.open("r+", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        header = next(reader)
        types = next(reader)

        rows = list(reader)

        for row in rows:
            row[header.index("Translation")] = row[header.index("Brazilian")]

        f.seek(0)
        f.truncate()
        writer = csv.writer(f)
        writer.writerows((header, types))
        writer.writerows(rows)


def _process_file(file: Path, loc_dir: Path):
    """Preenche as colunas de tradução fan-made com nossa tradução.

    Args:
        file: Arquivo da tradução fan-made.
        loc_dir: Pasta que contém os arquivos de tradução oficial.
    """
    with file.open(newline="", encoding="utf-8") as ts_f:
        ts_reader = csv.reader(ts_f)

        header = next(ts_reader)

        with (loc_dir / f"SOR Names - {file.stem}DB.csv").open(
            "r+", newline="", encoding="utf-8"
        ) as loc_f:
            loc_reader = csv.reader(loc_f)

            loc_header = next(loc_reader)

            # Esse código assume que o STRING_ID sempre será a primeira coluna
            if loc_header.index("STRING_ID") != 0:
                raise RuntimeError(
                    f"O arquivo {loc_dir.name} não tem o cabeçalho correto"
                )

            loc_ts_index = loc_header.index("Translation")

            loc_types = next(loc_reader)

            loc_rows = {row[0]: row[1:] for row in loc_reader}

            for row in ts_reader:
                if row[0] in loc_rows:
                    loc_rows[row[0]][loc_ts_index - 1] = row[
                        header.index("Translation")
                    ]
                else:
                    raise RuntimeError(
                        f"O STRING_ID {row[0]} não existe no arquivo {loc_dir.name}"
                    )

            loc_f.seek(0)
            loc_f.truncate()
            writer = csv.writer(loc_f)
            writer.writerows((loc_header, loc_types))
            writer.writerows((k, *v) for k, v in loc_rows.items())


def _main():
    print("É recomendado fazer um backup da pasta Localization antes de continuar.")

    while True:
        loc_path = Path(input("Caminho da pasta Localization: "))

        if loc_path.is_dir():
            break

        print("Caminho inválido, tente novamente")

    try:
        for file in loc_path.glob("*.csv"):
            _set_defaults(file)

        for file in (DIR / "tradução").glob("*.csv"):
            _process_file(file, loc_path)
    except BaseException as e:
        print(
            f"Erro ao processar os arquivos, eles podem ter sido corrompidos",
            file=sys.stderr,
        )
        raise


if __name__ == "__main__":
    _main()
