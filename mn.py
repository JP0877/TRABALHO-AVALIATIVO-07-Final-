import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Função para realizar a raspagem de dados
def scrape_patoloco():
    url = 'https://www.patoloco.com.br/cadeiras-gamer'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.find_all('div', class_='product-item')

        data = []
        for product in products:
            name = product.find('h2', class_='product-title').text.strip()
            price = product.find('span', class_='price').text.strip()
            rating = product.find('div', class_='ratings-result').text.strip()
            data.append({'Name': name, 'Price': price, 'Rating': rating})

        return data
    else:
        st.error(f'Failed to retrieve data. Status code: {response.status_code}')
        return None

# Função para criar um gráfico simples com matplotlib
def plot_data(df):
    plt.figure(figsize=(10, 6))
    plt.bar(df['Name'], df['Price'].str.replace('R$', '').astype(float))
    plt.xticks(rotation=45, ha='right')
    plt.title('Preços das Cadeiras Gamer')
    plt.xlabel('Nome do Produto')
    plt.ylabel('Preço (R$)')
    st.pyplot()

# Função para exportar dados para PDF
def export_to_pdf(df):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, 750, "Relatório de Preços das Cadeiras Gamer")

    pdf.setFont("Helvetica", 12)
    y = 700
    for index, row in df.iterrows():
        pdf.drawString(100, y, f"Nome: {row['Name']}")
        pdf.drawString(100, y - 20, f"Preço: {row['Price']}")
        pdf.drawString(100, y - 40, f"Avaliação: {row['Rating']}")
        y -= 60

    pdf.save()
    buffer.seek(0)
    return buffer

# Execução principal do Streamlit
def main():
    st.title('Análise de Cadeiras Gamer - Patoloco')

    # Raspagem de dados e criação do DataFrame
    data = scrape_patoloco()
    if data:
        df = pd.DataFrame(data)
        st.subheader('Dados das Cadeiras Gamer')
        st.write(df)

        # Visualização com matplotlib
        st.subheader('Visualização de Preços')
        plot_data(df)

        # Exportação para PDF
        st.subheader('Exportar para PDF')
        pdf_buffer = export_to_pdf(df)
        st.download_button('Baixar Relatório PDF', pdf_buffer, file_name='relatorio_cadeiras_gamer.pdf')

    else:
        st.error('Falha ao obter os dados. Tente novamente mais tarde.')

if __name__ == '__main__':
    main()
