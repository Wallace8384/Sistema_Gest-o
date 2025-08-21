import pandas as pd
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.produtos_file = 'produtos.xlsx'
        self.vendas_file = 'vendas.xlsx'
        self._inicializar_arquivos()
    
    def _inicializar_arquivos(self):
        # Inicializar arquivo de produtos
        if not os.path.exists(self.produtos_file):
            df_produtos = pd.DataFrame(columns=['id', 'nome', 'quantidade', 'valor_unitario', 'valor_total'])
            df_produtos.to_excel(self.produtos_file, index=False)
        
        # Inicializar arquivo de vendas
        if not os.path.exists(self.vendas_file):
            df_vendas = pd.DataFrame(columns=['produto', 'quantidade', 'valor_item', 'valor_total', 'data', 'hora'])
            df_vendas.to_excel(self.vendas_file, index=False)
    
    def autenticar_usuario(self, usuario, senha):
        # Usuário e senha padrão (em produção, usar banco seguro)
        usuarios = {'admin': 'admin123', 'user': 'user123'}
        return usuarios.get(usuario) == senha
    
    def cadastrar_produto(self, id_produto, nome, quantidade, valor_unitario):
        try:
            df = pd.read_excel(self.produtos_file)
            
            # Verificar se ID já existe
            if not df.empty and str(id_produto) in df['id'].astype(str).values:
                return False, "ID do produto já existe!"
            
            valor_total = quantidade * valor_unitario
            novo_produto = {
                'id': str(id_produto),  # Garantir que seja string
                'nome': nome,
                'quantidade': quantidade,
                'valor_unitario': valor_unitario,
                'valor_total': valor_total
            }
            
            # Corrigido: criar DataFrame com colunas explícitas para evitar o warning
            novo_df = pd.DataFrame([novo_produto])
            
            # Garantir que as colunas estejam na mesma ordem
            novo_df = novo_df[['id', 'nome', 'quantidade', 'valor_unitario', 'valor_total']]
            
            if df.empty:
                df = novo_df
            else:
                df = pd.concat([df, novo_df], ignore_index=True)
            
            df.to_excel(self.produtos_file, index=False)
            return True, "Produto cadastrado com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao cadastrar produto: {str(e)}"
    
    def realizar_venda(self, produto_id, quantidade_vendida):
        try:
            # Ler produtos
            df_produtos = pd.read_excel(self.produtos_file)
            
            if df_produtos.empty:
                return False, "Nenhum produto cadastrado!"
            
            # Converter ID para string para garantir compatibilidade
            produto_id_str = str(produto_id)
            
            # Encontrar produto - converter todos os IDs para string para comparação
            df_produtos['id'] = df_produtos['id'].astype(str)
            produto_idx = df_produtos[df_produtos['id'] == produto_id_str].index
            
            if len(produto_idx) == 0:
                # Debug: mostrar todos os IDs disponíveis
                ids_disponiveis = df_produtos['id'].tolist()
                print(f"IDs disponíveis: {ids_disponiveis}")
                print(f"ID procurado: {produto_id_str}")
                return False, f"Produto não encontrado! IDs disponíveis: {', '.join(ids_disponiveis)}"
            
            idx = produto_idx[0]
            produto = df_produtos.loc[idx]
            
            if produto['quantidade'] < quantidade_vendida:
                return False, f"Quantidade insuficiente em estoque! Disponível: {produto['quantidade']}"
            
            # Atualizar estoque
            nova_quantidade = produto['quantidade'] - quantidade_vendida
            df_produtos.at[idx, 'quantidade'] = nova_quantidade
            df_produtos.at[idx, 'valor_total'] = nova_quantidade * produto['valor_unitario']
            
            # Registrar venda
            df_vendas = pd.read_excel(self.vendas_file)
            
            nova_venda = {
                'produto': produto['nome'],
                'quantidade': quantidade_vendida,
                'valor_item': float(produto['valor_unitario']),
                'valor_total': float(quantidade_vendida * produto['valor_unitario']),
                'data': datetime.now().strftime('%Y-%m-%d'),
                'hora': datetime.now().strftime('%H:%M:%S')
            }
            
            # Corrigido: criar DataFrame com colunas explícitas
            nova_venda_df = pd.DataFrame([nova_venda])
            nova_venda_df = nova_venda_df[['produto', 'quantidade', 'valor_item', 'valor_total', 'data', 'hora']]
            
            if df_vendas.empty:
                df_vendas = nova_venda_df
            else:
                df_vendas = pd.concat([df_vendas, nova_venda_df], ignore_index=True)
            
            # Salvar alterações
            df_produtos.to_excel(self.produtos_file, index=False)
            df_vendas.to_excel(self.vendas_file, index=False)
            
            return True, f"Venda realizada com sucesso! Total: R$ {nova_venda['valor_total']:.2f}"
            
        except Exception as e:
            return False, f"Erro ao realizar venda: {str(e)}"
    
    def consultar_estoque(self):
        try:
            df = pd.read_excel(self.produtos_file)
            if df.empty:
                return []
            
            # Garantir que IDs sejam strings para exibição
            df['id'] = df['id'].astype(str)
            return df[['id', 'nome', 'quantidade']].to_dict('records')
        except Exception as e:
            print(f"Erro ao consultar estoque: {e}")
            return []
    
    def relatorio_vendas_dia(self):
        try:
            df = pd.read_excel(self.vendas_file)
            if df.empty:
                return {'total_vendas': 0, 'valor_total': 0, 'vendas_detalhes': []}
            
            hoje = datetime.now().strftime('%Y-%m-%d')
            vendas_hoje = df[df['data'] == hoje]
            
            total_vendas = len(vendas_hoje)
            valor_total = vendas_hoje['valor_total'].sum() if not vendas_hoje.empty else 0
            
            return {
                'total_vendas': total_vendas,
                'valor_total': float(valor_total),
                'vendas_detalhes': vendas_hoje.to_dict('records')
            }
        except Exception as e:
            print(f"Erro ao gerar relatório: {e}")
            return {'total_vendas': 0, 'valor_total': 0, 'vendas_detalhes': []}
    
    # Método auxiliar para debug - listar todos os produtos
    def listar_produtos(self):
        try:
            df = pd.read_excel(self.produtos_file)
            if df.empty:
                return "Nenhum produto cadastrado"
            
            df['id'] = df['id'].astype(str)
            return df[['id', 'nome', 'quantidade', 'valor_unitario']].to_string(index=False)
        except Exception as e:
            return f"Erro ao listar produtos: {e}"
        