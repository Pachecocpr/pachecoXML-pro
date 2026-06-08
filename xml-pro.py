import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
import io

# Configuração da página do Streamlit
st.set_page_config(page_title="Conversor para XML", page_icon="📄", layout="centered")

st.title("🔄 Conversor de TXT e Excel para XML")
st.write("Abra seus arquivos .txt ou .xlsx/.xls e baixe a versão convertida em XML.")

# Função para embelezar o XML gerado (identação automática)
def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")

# Função para converter DataFrame (Excel/TXT estruturado) para XML
def dataframe_to_xml(df, root_name="dados", row_name="item"):
    root = ET.Element(root_name)
    
    for _, row in df.iterrows():
        row_element = ET.SubElement(root, row_name)
        for col in df.columns:
            child = ET.SubElement(row_element, str(col).replace(" ", "_")) # Substitui espaços por _ nas tags
            child.text = str(row[col])
            
    return prettify(root)

# Componente de Upload do Streamlit
uploaded_file = st.file_uploader("Escolha um arquivo TXT ou Excel", type=["txt", "xlsx", "xls"])

if uploaded_file is not None:
    file_details = {"Nome do arquivo": uploaded_file.name, "Tipo": uploaded_file.type}
    st.write(file_details)
    
    try:
        df = None
        # Verifica a extensão do arquivo
        if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.txt'):
            # Tenta ler como TXT delimitado (ajuste o sep se for ponto e vírgula, ex: sep=';')
            df = pd.read_csv(uploaded_file, sep="\t", header=None)
            # Se ler apenas uma coluna, renomeia para 'linha'
            if len(df.columns) == 1:
                df.columns = ['linha_texto']
        
        if df is not None:
            st.success("Arquivo carregado com sucesso! Pré-visualização dos dados:")
            st.dataframe(df.head()) # Mostra as primeiras linhas na tela
            
            # Gera o XML
            xml_data = dataframe_to_xml(df)
            
            # Botão de Download do XML gerado
            st.download_button(
                label="📥 Baixar arquivo XML",
                data=xml_data,
                file_name=f"{uploaded_file.name.split('.')[0]}.xml",
                mime="application/xml"
            )
            
            # Mostrar uma prévia do XML na tela
            with st.expander("Ver prévia do código XML gerado"):
                st.code(xml_data, language='xml')
                
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
