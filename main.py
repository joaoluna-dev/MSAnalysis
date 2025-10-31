from pathlib import Path
import os
import pandas as pd
import matplotlib.pyplot as plt

def parse_table_files(filepath, extension, threshold, filename):
    if extension == ".xlsx":
        df = pd.read_excel(filepath, sheet_name="Summary Report", engine="openpyxl")
        df = df.fillna("NA")
        df = df[df['Confidence'] >= threshold]
        df = df.sort_values(by='Confidence', ascending=False)
    return df

def plot_data(df, file_name):
    df20 = df.head(20)
    confidence_score = df20['Confidence']
    mol_name = df20['Library Match']
    plt.barh(mol_name, confidence_score, color="#4CAF50")
    plt.xlabel("Moléculas encontradas")
    plt.ylabel("Confiança", fontsize=5)
    plt.title(f"Top 20 moléculas com maior escore de confiança em {file_name}")
    plt.savefig(f"{file_name}.tiff", dpi=300)

def main():
    while True:
        summary_file = "Resumo_análises.xlsx"
        input_folder = Path(input("Insira o caminho da pasta com as planilhas obtidas da análise de GC-MS: "))
        if not os.path.exists(input_folder):
            print("O caminho inserido não existe. Tente novamente.")
            continue
        extension_type = input("Insira o formato dos arquivos das planilhas, com ponto (ex: .xlsx): ").lower()
        while True:
            threshold = int(input("Insira o limiar de match dos compostos para a análise (ex: 70, 90, 100...): "))
            if threshold > 100:
                print(f"Limiar inválido inserido: {threshold}")
                continue
            else:
                break

        table_files = [file for file in os.listdir(input_folder) if extension_type in file and "~" not in file and "#" not in file]
        print(f"Arquivos localizados: {table_files}")
        if len(table_files) == 0:
            print("O diretório inserido não possui nenhum arquivo do tipo especificado.")
            continue
        with pd.ExcelWriter(summary_file, engine='openpyxl') as writer:
            for table in table_files:
                print(f"Analisando: {table}...")
                file_path = os.path.join(input_folder, table)
                file_name = Path(file_path).stem
                if os.path.getsize(file_path) == 0:
                    print(f"O arquivo {table} está vazio. Verifique o conteúdo do arquivo.")
                    continue
                filtered_file = parse_table_files(filepath=file_path, extension=extension_type, threshold=threshold, filename=file_name)
                plot_data(df=filtered_file, file_name=file_name)
                filtered_file.to_excel(writer, sheet_name=file_name, index=False)
        print("Análise dos arquivos concluída.")

if __name__ == '__main__':
    main()
