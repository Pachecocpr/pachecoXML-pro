import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
import io

# Configuração da página do Streamlit
st.set_page_config(page_title="Conversor para XML", page_icon="📄", layout="centered")

st.title("🔄 Conversor (UTF-8 / Pipe) para XML")
st.write("Suporta arquivos Excel ou arquivos TXT/CSV separados por **Pipe (|)** salvando em **UTF-8**.")

# Função para formatar o XML com indentação limpa
def prettify(elem):
    # Converte para string forçando a codificação UTF-8
    rough_string = ET.tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    # Retorna o XML formatado como string UTF-8
    return reparsed.toprettyxml(indent="    ", encoding="utf-8").decode("utf-8")

# Função para converter o DataFrame para o formato XML
def dataframe_to_xml(df, root_name="dados", row_name="item"):
    root = ET.Element(root_name)
    
    for _, row in df.iterrows():
        row_element = ET.SubElement(root, row_name)
        for col in df.columns:
            # Garante que os nomes das tags não tenham espaços ou caracteres inválidos
            tag_name = str(col).strip().replace(" ", "_").replace("|", "_")
            child = ET.SubElement(row_element, tag_name)
            child.text = str(row[col])
            
    return prettify(root)

# Componente de Upload
uploaded_file = st.file_uploader("Escolha um arquivo TXT, CSV ou Excel", type=["txt", "csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = None
        filename = uploaded_file.name.lower()
        
        # 1. Se for EXCEL
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(uploaded_file)
            
        # 2. Se for TXT ou CSV (Configurado para UTF-8 e Separador Pipe '|')
        elif filename.endswith('.txt') or filename.endswith('.csv'):
            df = pd.read_csv(
                uploaded_file, 
                sep="|",          # <--- Define o separador como PIPE
                encoding="utf-8", # <--- Força a leitura em UTF-8
                engine="python"   # Evita bugs de leitura com separadores especiais
            )
        
        if df is not None:
            st.success("Arquivo processado com sucesso!")
            
            # Mostra a tabela na tela para conferência
            st.subheader("📋 Pré-visualização dos Dados")
            st.dataframe(df.head()) 
            
            # Gera o XML tratado em UTF-8
            xml_data = dataframe_to_xml(df)
            
            # Botão de Download do XML gerado
            st.subheader("💾 Baixar Resultado")
            st.download_button(
                label="📥 Baixar arquivo XML (UTF-8)",
                data=xml_data,
                file_name=f"{uploaded_file.name.split('.')[0]}.xml",
                mime="application/xml"
            )
            
            # Mostra uma prévia do código na tela
            with st.expander("Ver prévia do código XML gerado"):
                st.code(xml_data, language='xml')
                
    except UnicodeDecodeError:
        st.error("❌ Erro de codificação! Certifique-se de que o seu arquivo de origem foi salvo como UTF-8.")
    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")
