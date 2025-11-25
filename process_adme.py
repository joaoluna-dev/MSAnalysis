# Parsing and plotting data from ADMET .csv files

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def read_csv_and_plot_data(dataframe: pd.DataFrame, colname: str, plotfolder: str, filename: str):
    print(f"Iniciando plotagem de {colname}...")
    df = dataframe.sort_values(by=colname, ascending=False)
    x = df[colname]
    plt.figure(figsize=(17,10))
    plot = sns.barplot(x=x)
    plot.set_xlabel(f"{colname}")
    plot.set_ylabel("Count")
    plot.set_title(f"Análise de {colname}")
    plt.tight_layout()
    plt.savefig(os.path.join(plotfolder, f"{file}.tiff"), dpi=300, format='tiff', bbox_inches='tight')
    plt.close()
    print(f'Gráfico {file} criado.')

groups_analysis = [
        "CYP1A2_inhibitor",
        "CYP2C19_inhibitor",
        "CYP2C9_inhibitor",
        "CYP2D6_inhibitor",
        "CYP3A4_inhibitor"
    ],
rules_violations = [
        "lipinski_violations",
        "ghose_violations",
        "veber_violations",
        "eagan_violations",
        "muegge_violations"]



input_folder = input("Insira o caminho com os arquivos .csv: ")
for file in os.listdir(input_folder):
    if ".csv" in file:
        file = os.path.join(input_folder, file)
        df = pd.read_csv(file)
        read_csv_and_plot_data(dataframe=data, colname=analysis, plotfolder=input_folder, filename=os.path.splitext(file)[0])
