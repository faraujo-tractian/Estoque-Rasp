import pandas as pd
import sys

# Ler o arquivo Excel
file_path = "Inventário de Recursos Operacionais da Qualidade _ 5S.xlsx"

try:
    # Carregar o Excel
    excel_file = pd.ExcelFile(file_path)
    
    print("=" * 80)
    print(f"ARQUIVO: {file_path}")
    print("=" * 80)
    
    # Mostrar todas as abas
    print(f"\nABAS ENCONTRADAS: {len(excel_file.sheet_names)}")
    for i, sheet in enumerate(excel_file.sheet_names, 1):
        print(f"  {i}. {sheet}")
    
    # Ler cada aba
    for sheet_name in excel_file.sheet_names:
        print("\n" + "=" * 80)
        print(f"ABA: {sheet_name}")
        print("=" * 80)
        
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        print(f"\nLinhas: {len(df)} | Colunas: {len(df.columns)}")
        print(f"\nCOLUNAS:")
        for col in df.columns:
            print(f"  - {col}")
        
        print(f"\nPRIMEIRAS 5 LINHAS:")
        print(df.head().to_string())
        
        # Dados não-nulos
        print(f"\nDADOS NAO-NULOS POR COLUNA:")
        print(df.count().to_string())
            
except Exception as e:
    print(f"ERRO ao ler arquivo: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

