import csv
import plotly.express as px

def carregar_dados(nome_arquivo):
    armas = []
    with open(nome_arquivo, mode='r', encoding='utf-8') as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            try:
                linha['TotalDamage'] = float(linha.get('TotalDamage', 0) or 0)
                linha['CritChance'] = float(linha.get('CritChance', 0) or 0)
                linha['FireRate'] = float(linha.get('FireRate', 0) or 0)
                linha['Slash'] = float(linha.get('Slash', 0) or 0)
                linha['Viral'] = float(linha.get('Viral', 0) or 0)
            except ValueError:
                pass 

            armas.append(linha)
    return armas

def menu():
    print("\n" + "="*50)
    print(" SISTEMA DE ANÁLISE DE ARSENAL - WARFRAME ")
    print("="*50)
    print("1. Agrupar armas por Slot (Primária/Secundária) e exibir Top 10 Dano")
    print("2. Ordenar todas as armas por Chance Crítica (Top 20)")
    print("3. Comparar 2 armas específicas")
    print("4. Analisar armas por tipo de dano (Conjuntos: Intersecção/Diferença)")
    print("5. Gerar Gráfico de Barras (Média de Dano por Slot) - Plotly")
    print("6. Gerar Gráfico de Dispersão (Taxa de Tiro x Dano) - Plotly")
    print("0. Sair")
    print("="*50)
    return input("Escolha uma opção: ")

def main():
    dataset = carregar_dados('warface_weapons.csv') 
    
    while True:
        opcao = menu()
        
        if opcao == '0':
            print("Encerrando o programa...")
            break
            
        elif opcao == '1':
            slot_desejado = input("Digite o Slot da arma (ex: Primary, Secondary, Arch-Gun): ")
            armas_filtradas = [arma for arma in dataset if arma.get('Slot') == slot_desejado]
            armas_ordenadas = sorted(armas_filtradas, key=lambda x: x['TotalDamage'], reverse=True)
            
            print(f"\n--- Top 10 Armas do Slot {slot_desejado} por Dano ---")
            for i, arma in enumerate(armas_ordenadas[:10], 1):
                print(f"{i}. {arma.get('Name')} - Dano: {arma['TotalDamage']}")

        elif opcao == '2':
            armas_ordenadas = sorted(dataset, key=lambda x: x['CritChance'], reverse=True)
            
            print("\n--- Top 20 Armas com Maior Chance Crítica ---")
            for i, arma in enumerate(armas_ordenadas[:20], 1):
                print(f"{i}. {arma.get('Name')} - Chance Crítica: {arma['CritChance']}")

        elif opcao == '3':
            nome1 = input("Digite o nome da primeira arma: ")
            nome2 = input("Digite o nome da segunda arma: ")
            
            arma1 = next((a for a in dataset if a.get('Name', '').lower() == nome1.lower()), None)
            arma2 = next((a for a in dataset if a.get('Name', '').lower() == nome2.lower()), None)
            
            if arma1 and arma2:
                soma_dano = arma1['TotalDamage'] + arma2['TotalDamage']
                media_dano = soma_dano / 2
                diferenca = abs(arma1['TotalDamage'] - arma2['TotalDamage'])
                
                print(f"\n--- Comparação: {arma1.get('Name')} vs {arma2.get('Name')} ---")
                print(f"Dano {arma1.get('Name')}: {arma1['TotalDamage']}")
                print(f"Dano {arma2.get('Name')}: {arma2['TotalDamage']}")
                print(f"Soma dos Danos: {soma_dano}")
                print(f"Média entre as duas: {media_dano}")
                print(f"Diferença de Dano: {diferenca}")
            else:
                print("Uma ou ambas as armas não foram encontradas. Verifique o nome digitado.")

        elif opcao == '4':
            set_slash = {arma.get('Name') for arma in dataset if arma['Slash'] > 0}
            set_viral = {arma.get('Name') for arma in dataset if arma['Viral'] > 0}
            
            print("\n1. Intersecção: Armas que dão dano Slash E Viral simultaneamente")
            print("2. Diferença: Armas que dão dano Slash MAS NÃO dão Viral")
            sub_op = input("Escolha a operação de conjunto: ")
            
            if sub_op == '1':
                resultado = set_slash.intersection(set_viral)
                print(f"\nEncontradas {len(resultado)} armas com Slash e Viral.")
                print(list(resultado)[:15]) 
            elif sub_op == '2':
                resultado = set_slash.difference(set_viral)
                print(f"\nEncontradas {len(resultado)} armas APENAS com Slash (sem Viral).")
                print(list(resultado)[:15])
            else:
                print("Opção inválida.")

        elif opcao == '5':
            slots = {}
            for arma in dataset:
                s = arma.get('Slot')
                if s:
                    if s not in slots:
                        slots[s] = {'soma': 0, 'qtd': 0}
                    slots[s]['soma'] += arma['TotalDamage']
                    slots[s]['qtd'] += 1
            
            categorias = list(slots.keys())
            medias = [slots[c]['soma'] / slots[c]['qtd'] for c in categorias]
            
            dados_grafico_barras = {
                'Slot da Arma': categorias,
                'Dano Médio': medias
            }
            
            fig = px.bar(dados_grafico_barras, 
                         x='Slot da Arma', 
                         y='Dano Médio', 
                         title='Média de Dano por Slot de Arma (TotalDamage)',
                         color='Slot da Arma')
            fig.show()

        elif opcao == '6':
            dados_validos = [a for a in dataset if a['TotalDamage'] > 0 and a['FireRate'] > 0]
            
            fire_rates = [a['FireRate'] for a in dados_validos]
            damages = [a['TotalDamage'] for a in dados_validos]
            nomes = [a.get('Name') for a in dados_validos]
            
            dados_grafico_dispersao = {
                'Taxa de Tiro (FireRate)': fire_rates,
                'Dano Base (TotalDamage)': damages,
                'Nome da Arma': nomes
            }
            
            fig = px.scatter(dados_grafico_dispersao, 
                             x='Taxa de Tiro (FireRate)', 
                             y='Dano Base (TotalDamage)', 
                             title='Relação: Taxa de Tiro vs Dano Base',
                             hover_name='Nome da Arma',
                             opacity=0.6)
            fig.show()
            
        else:
            print("Opção inválida! Tente novamente.")

if __name__ == "__main__":
    main()