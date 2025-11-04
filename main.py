from pathlib import Path
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pubchempy as pcp

def parse_table_files(filepath, extension, threshold, filename):
    if extension == ".xlsx":
        df = pd.read_excel(filepath, sheet_name="Summary Report", engine="openpyxl")
        df = df.fillna("NA")
        if 'Confidence' in df:
            df = df[df['Confidence'] >= threshold]
            df = df.sort_values(by='Confidence', ascending=False)
        else:
            print(f"O arquivo {filename} não possui dados padronizados de GC-MS.")
            df = pd.DataFrame()
    return df

def plot_data(df, file_name, plotfolder):
    print(f"Iniciando plotagem de {file_name}...")
    df = df.sort_values(by='Confidence', ascending=False)
    confidence_score = df['Confidence']
    mol_name = df['Library Match']
    plt.figure(figsize=(17,10))
    mol_plot = sns.barplot(x=confidence_score, y=mol_name, orient='h')
    mol_plot.set_xlabel("Confiança")
    plt.ylabel("Moléculas")
    mol_plot.set_title(f"Moléculas X escore de confiança em {file_name}")
    plt.tight_layout()
    plt.savefig(os.path.join(plotfolder, f"{file_name}.tiff"), dpi=300, format='tiff', bbox_inches='tight')
    plt.close()
    print(f'Gráfico {file_name} criado.')

def unite_data(summary, repslist, extension, colname, allreps):
    molnames = set()
    for rep in repslist:
        if rep in allreps:
            data = pd.read_excel(summary, sheet_name=rep, engine="openpyxl")
            data = data['Library Match']
            molnames.update(data)
            print(f"Amostra {rep} analisada.")
        else:
            print(f"A replicata {rep} não foi localizada, tente novamente.")
            return "\n"
    mol_list = list(molnames)
    mol_string = "/".join(mol_list)
    new_item = f"{colname}: {mol_string}\n"
    print(new_item)
    return new_item

def get_smiles(mol, smilesfile):
    print(f"Obtendo dados da molécula {mol}...")
    compound = pcp.get_compounds(mol, "name")
    if len(compound) > 0:
        compound = compound[0]
        if compound:
            with open(smilesfile, 'a') as sm_file:
                sm_file.write(f"{mol}\n")
                sm_file.write(f"CID: {compound.cid}\n")
                sm_file.write(f"SMILES: {compound.smiles}\n")
                sm_file.write("-------------------------------------------\n")
            print(f"SMILES e CID de {mol} obtidos.")
        else:
            print(f"Molécula {mol} não identificada no PUBCHEM. Verifique e tente novamente manualmente.")
    else:
        print(f"A busca pela molécula {mol} não retornou resultados. Tente novamente manualmente mais tarde.")
        with open(smilesfile, 'a') as sm_file:
            sm_file.write(f"{mol}\n")
            sm_file.write(f"A busca pela molécula {mol} não retornou resultados. Tente novamente manualmente mais tarde.\n")
            sm_file.write("-------------------------------------------\n")


def main():
    while True: #Loop principal

        #Obtenção do diretório com os dados de análise de GC-MS, e limiar de análise
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

        #Criar arquivo xlsx que conterá as moléculas selecionadas
        summary_file = os.path.join(input_folder, "Resumo_análises.xlsx")

        #Leituras de arquivos com os dados de análise de GC-MS
        table_files = [file for file in os.listdir(input_folder) if extension_type in file and "~" not in file and "#" not in file] #Lê os arquivos da extensão selecionada pelo usuário, no diretório fornecido
        print(f"Arquivos localizados: {table_files}")
        if len(table_files) == 0: #Caso não hajam arquivos do tipo especificado pelo usuário
            print("O diretório inserido não possui nenhum arquivo do tipo especificado.")
            continue

        #Cria pasta onde estarão os gráficos, plots
        plot_folder = os.path.join(input_folder, "plots")
        if not os.path.exists(plot_folder):
            os.mkdir(plot_folder)

        #Leitura dos arquivos, filtragem das moléculas, plotagem dos gráficos e escrita em arquivo com as moléculas selecionadas
        with pd.ExcelWriter(summary_file, engine='openpyxl') as writer: #Abre o arquivo que contém as moléculas selecionadas
            for table in table_files: #Itera sobre os arquivos da extensão selecionada no diretório definido pelo usuário
                print(f"Analisando: {table}...")
                file_path = os.path.join(input_folder, table) #Obtém o caminho absoluto do arquivo selecionado
                file_name = Path(file_path).stem #Obtém o nome do arquivo selecionado
                if os.path.getsize(file_path) == 0: #Verifica se o arquivo selecionado está vazio
                    print(f"O arquivo {table} está vazio. Verifique o conteúdo do arquivo.")
                    continue
                filtered_file = parse_table_files(filepath=file_path, extension=extension_type, threshold=threshold, filename=file_name) #Passa o arquivo para a função filtered_table, que lê os arquivos e filtra as moléculas com base no threshold definido
                plot_data(df=filtered_file, file_name=file_name, plotfolder=plot_folder) #Plota o gráfico com os dados obtidos nos arquivos na pasta de trabalho, em uma pasta plots
                filtered_file.to_excel(writer, sheet_name=file_name, index=False) #Escreve as moléculas no arquivo de moléculas selecionadas
        print("Análise dos arquivos concluída.")

        #Criação do arquivo que conterá as moléculas das replicatas
        joined_molecules_file = os.path.join(input_folder, "Moléculas_únicas.txt")

        #Escreve o header do arquivo que conterá as moléculas das replicatas
        with open(joined_molecules_file, "w") as mol_file:
            mol_file.write("Moléculas únicas entre as replicatas: \n")
            mol_file.write("\n")

        #Obtém as replicatas do estudo
        available_reps = pd.ExcelFile(summary_file).sheet_names

        #Escrita das moléculas comuns às replicatas da amostra
        data_groups = {}
        with open(joined_molecules_file, "a") as mol_file:
            while True:
                #Exibe todas as replicatas disponíveis no estudo
                print("Replicatas disponíveis: ")
                available_reps.sort()
                print(f"{", ".join(available_reps)}")
                #Solicita o nome das replicatas do mesmo grupo
                reps_string = input("Insira o nome das replicatas da mesma amostra, que correspondem às replicatas, separados por vírgula, sem a extensão. Caso finalizado, aperte enter.: ")
                if reps_string: #Verifica se houve o input, caso houve
                    print(f"Analisando: {reps_string}")
                    reps_list = [p.strip(" ").strip("'").strip('"') for p in reps_string.split(',') if p.strip()] #Trata a string obtida, transformando ela em uma lista
                    data_group = unite_data(summary=summary_file, repslist=reps_list, extension=".xlsx", colname=reps_string, allreps=available_reps) #Passa para a função que faz a comparação entre as replicatas da amostra, para entender quais moléculas estão presentes nas análises, e reunir sem duplicatas
                    mol_file.write(data_group) #Escreve os dados obtidos (replicatas: moléculas)
                    mol_file.write("\n") #Escreve quebra de linha para facilitar a leitura
                    data_group_list = data_group.split(":")
                    data_groups[data_group_list[0]] = data_group_list[1].split("/")
                    print(f"Replicatas {reps_string} analisadas.")
                    continue
                else: #Caso não haja o input (usuário apertou enter, decidindo encerrar)
                    selection_finish_reps = input("Deseja encerar o estudo das replicatas? (y/n): ").lower()
                    if selection_finish_reps == "y":
                        break
                    elif selection_finish_reps == "n":
                        continue
                    else:
                        print(f"Seleção inválida: {selection_finish_reps}")
                        continue
        print("Análise das replicatas concluída.")

        #Criação de pasta que conterá os arquivos .SDF das moléculas
        sdf_folder = os.path.join(input_folder, "SDF_files")
        if not os.path.exists(sdf_folder):
            os.mkdir(sdf_folder)

        #Criação de arquivo com os SMILES das moléculas
        smiles_file = os.path.join(input_folder, "SMILES.txt")
        with open(smiles_file, 'w') as sm_file:
            sm_file.write("Moléculas e seus smiles: \n")

        #Parsing do dicionário com as moléculas de cada amostra
        for chave in data_groups:
            print(f"Analisando amostra {chave}...")
            data_molecules = data_groups[chave] #Obtém a lista de moléculas relacionadas à cada estudo de replicatas/amostra isolada
            with open(smiles_file, 'a') as sm_file:
                sm_file.write(f"{chave}:\n")
                sm_file.write("\n")
                for molecule in data_molecules: #Itera sobre as moléculas de cada lista
                    get_smiles(mol=molecule, smilesfile=smiles_file) #Obtém os SMILES e o CID de cada molécula
                    # get_sdf(mol=molecule, filesfolder=sdf_folder) #Obtém o arquivo .SDF de cada molécula
        print("Dados das moléculas obtidos no PUBCHEM.")



if __name__ == '__main__':
    main()
