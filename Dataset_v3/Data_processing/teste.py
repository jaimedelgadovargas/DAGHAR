from typing import List, Dict
from pathlib import Path
import numpy as np
import pandas as pd

def read_hiacc_smartphone(hiacc_path: str) -> pd.DataFrame:
    """
    Parâmetros
    ----------
    hiacc_path : str
        Caminho para a pasta raiz "HIAAC".
        
    Retorna
    -------
    pd.DataFrame
        DataFrame contendo as colunas:
          - accel-x, accel-y, accel-z
          - gyro-x, gyro-y, gyro-z
          - timestamp-server-accel, timestamp-server-gyro (ajustados para iniciar em 0)
          - activity code, user, window, pos
    """
    hiacc_path = Path(hiacc_path)
    
    # Pastas de posição
    positions: List[str] = ["Bolso_direito", "Mochila"]
    
    # Colunas esperadas nos arquivos CSV
    feature_columns_acc = ["Timestamp Server", "Value 1", "Value 2", "Value 3"]
    feature_columns_gyr = ["Timestamp Server", "Value 1", "Value 2", "Value 3"]
    
    dfs = []
    print("Iniciando leitura do dataset HIACC...")
    
    for pos in positions:
        pos_path = hiacc_path / pos
        if not pos_path.exists():
            continue
        
        for user_folder in sorted(pos_path.iterdir()):
            if not user_folder.is_dir():
                continue
            try:
                user = int(user_folder.name)
            except ValueError:
                continue
            # Processa apenas o usuário 1 para depuração
            if user != 1:
                continue
            
            # Define os arquivos conforme a posição
            if pos == "Bolso_direito":
                acc_file = user_folder / "Accelerometer_Bolso Direito.csv"
                gyr_file = user_folder / "Gyroscope_Bolso Direito.csv"
            elif pos == "Mochila":
                acc_file = user_folder / "Accelerometer_Mochila.csv"
                gyr_file = user_folder / "Gyroscope_Mochila.csv"
            else:
                continue
            if not acc_file.exists() or not gyr_file.exists():
                continue
            
            try:
                df_acc = pd.read_csv(acc_file, engine="python")
                df_acc["timestamp-server-accel"] = df_acc["Timestamp Server"].astype(np.int64)
                df_acc = df_acc[["timestamp-server-accel", "Value 1", "Value 2", "Value 3"]].copy()
                df_acc.columns = ["timestamp-server-accel", "accel-x", "accel-y", "accel-z"]
                df_acc["user"] = user
                df_acc["pos"] = pos
            except Exception:
                continue
            
            try:
                df_gyr = pd.read_csv(gyr_file, engine="python")
                df_gyr["timestamp-server-gyro"] = df_gyr["Timestamp Server"].astype(np.int64)
                df_gyr = df_gyr[["timestamp-server-gyro", "Value 1", "Value 2", "Value 3"]].copy()
                df_gyr.columns = ["timestamp-server-gyro", "gyro-x", "gyro-y", "gyro-z"]
                df_gyr["user"] = user
            except Exception:
                continue
            
            # Ajusta para que o giroscópio tenha o mesmo número de amostras que o acelerômetro
            len_min = min(len(df_acc), len(df_gyr))
            df_acc = df_acc.iloc[:len_min].reset_index(drop=True)
            df_gyr = df_gyr.iloc[:len_min].reset_index(drop=True)
            
            # Ajusta os timestamps para iniciar em 0 (milissegundos)
            df_acc["timestamp-server-accel"] -= df_acc["timestamp-server-accel"].iloc[0]
            df_gyr["timestamp-server-gyro"] -= df_gyr["timestamp-server-gyro"].iloc[0]
            
            # Leitura do arquivo de labels
            label_file = user_folder / f"{user_folder.name}_label_vitor.csv"
            if not label_file.exists():
                continue
            try:
                df_label = pd.read_csv(label_file)
                if "L" not in df_label.columns:
                    continue
                df_label["L"] = df_label["L"].astype(str).str.strip()
                df_label["activity code"] = df_label["L"]
            except Exception:
                continue
            
            # Define número de janelas (cada janela = 300 amostras)
            num_windows = min(len(df_acc) // 300, len(df_label))
            df_acc = df_acc.iloc[:num_windows * 300].reset_index(drop=True)
            df_gyr = df_gyr.iloc[:num_windows * 300].reset_index(drop=True)
            df_label = df_label.iloc[:num_windows].reset_index(drop=True)
            
            # Cria a coluna 'trial' para identificar cada janela
            df_acc["trial"] = df_acc.index // 300            
                     
            
            try:
                # Merge dos labels com o acelerômetro (inner on "trial")
                df_acc = df_acc.merge(
                df_label[["activity code"]].reset_index().rename(columns={"index": "trial"}),
                on="trial",
                how="inner"
                ).reset_index(drop=True)

                # Combina os dados dos sensores
                data_df = pd.concat([df_acc, df_gyr], axis=1)

            except Exception:
                continue
            
            dfs.append(data_df)
    
    if dfs:
        df_final = pd.concat(dfs, ignore_index=True)
    else:
        df_final = pd.DataFrame()
    
    print("Processamento concluído.")
    return df_final, dfs
