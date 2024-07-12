import certifi
import urllib3
import requests
import streamlit as st
from bs4 import BeautifulSoup
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def realizar_raspagem_amazon():
    url = "https://www.amazon.com.br/s?k=camisas"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Verifica se houve algum erro na requisição
        soup = BeautifulSoup(response.content, 'html.parser')
        produtos = soup.find_all('div', {'data-component-type': 's-search-result'})
        dados = []
        for produto in produtos:
            titulo = produto.find('span', {'class': 'a-size-base-plus a-color-base a-text-normal'})
            preco = produto.find('span', {'class': 'a-price-whole'})
            if titulo and preco:
                dados.append({
                    'Título': titulo.text.strip(),
                    'Preço': float(preco.text.replace('.', '').replace(',', '.'))  
                })
        return dados
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao acessar a página da Amazon: {e}")
        return None

def realizar_raspagem_mercado_livre():
    url = "https://lista.mercadolivre.com.br/camisas#D[A:camisas]"
   
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    try:
        response = http.request('GET', url)
        if response.status == 200:
            soup = BeautifulSoup(response.data, 'html.parser')
            produtos = soup.find_all('li', {'class': 'ui-search-layout__item'})
            dados = []
            for produto in produtos:
                titulo = produto.find('span', {'class': 'ui-search-item__title'})
                preco = produto.find('span', {'class': 'price-tag-fraction'})
                if titulo and preco:
                    dados.append({
                        'Título': titulo.text.strip(),
                        'Preço': float(preco.text.replace('.', '').replace(',', '.'))  
                    })
            return dados
        else:
            st.error(f"Erro ao acessar a página do Mercado Livre. Código de status: {response.status}")
            return None
    except Exception as e:
        st.error(f"Erro ao acessar a página do Mercado Livre: {e}")
        return None

def realizar_raspagem_shopee():
    url = "https://shopee.com.br/search?keyword=camisas"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Verifica se houve algum erro na requisição
        soup = BeautifulSoup(response.content, 'html.parser')
        produtos = soup.find_all('div', {'class': 'col-xs-2-4 shopee-search-item-result__item'})
        dados = []
        for produto in produtos:
            titulo = produto.find('div', {'class': 'yQmmFK _1POlWt _36CEnF'})
            preco = produto.find('span', {'class': '_29R_un'})
            if titulo and preco:
                dados.append({
                    'Título': titulo.text.strip(),
                    'Preço': float(preco.text.replace('.', '').replace(',', '.'))  
                })
        return dados
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao acessar a página da Shopee: {e}")
        return None

def exportar_para_pdf(dados, site):
    filename = f'dados_camisas_{site.lower().replace(" ", "_")}.pdf'
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, f'Camisas no {site}')
    c.setFont("Helvetica", 12)
    y = 700
    for i, dado in enumerate(dados, 1):
        c.drawString(100, y, f"Produto {i}:")
        c.drawString(120, y - 20, f"Título: {dado['Título']}")
        c.drawString(120, y - 40, f"Preço: R$ {dado['Preço']:.2f}")  
        y -= 60
    c.save()
    return filename  

def main():
    st.title("Análise e Exportação de Camisas")

    site_escolhido = st.selectbox('Escolha o site para realizar a raspagem de dados:', ['Amazon', 'Mercado Livre', 'Shopee'])

    if st.button(f'Realizar Raspagem de Dados no {site_escolhido}'):
        dados = None
        if site_escolhido == 'Amazon':
            dados = realizar_raspagem_amazon()
        elif site_escolhido == 'Mercado Livre':
            dados = realizar_raspagem_mercado_livre()
        elif site_escolhido == 'Shopee':
            dados = realizar_raspagem_shopee()

        if dados:
            st.text('Exemplo de dados extraídos:')
            for dado in dados:
                st.text(f"Título: {dado['Título']}, Preço: R$ {dado['Preço']:.2f}")
          
            if st.button(f'Exportar para PDF ({site_escolhido})'):
                filename = exportar_para_pdf(dados, site_escolhido)
                st.success(f'Dados exportados para {filename}.')
        else:
            st.error('Não foi possível obter os dados.')

if __name__ == "__main__":
    main()
