# **Português Brasileiro:**

Projeto: PANOPTES PATROL
Versão: 0.0.9
Autores: Fernando Nillsson Cidade

Descrição:
Este projeto é um gerenciador de arquivos e pastas que monitora mudanças em um diretório específico e exibe essas mudanças em uma interface gráfica. Ele é capaz de detectar operações como adição, exclusão, modificação, renomeação e movimentação de arquivos e pastas. Além disso, o projeto oferece funcionalidades para filtrar, exportar dados e gerar estatísticas sobre as operações realizadas.

MANUAL DE UTILIZAÇÃO RÁPIDO:

Como usar:
1. Execute o aplicativo para iniciar a interface gráfica.
2. Selecione um diretório para monitorar.
3. Utilize os botões e menus para iniciar/parar o monitoramento, aplicar filtros, exportar dados e visualizar estatísticas.

MANUAL DE UTILIZAÇÃO DETALHADO:

Requisitos do Sistema:
    - Sistema Operacional: Windows 10 ou superior.

Instalação:
    - Instale o arquivo executável do programa, siga as instruções do instalador e execute o programa.

Configuração Inicial:
    - A interface será exibida com a tabela de monitoramento vazia.
    - O idioma padrão será selecionado de acordo com a configuração do sistema.
    - Observe a barra lateral esquerda para acessar as funções principais.

Monitoramento de Diretórios:
    1. Selecionar um Diretório:
       - Clique no botão "Selecionar Diretório" ou selecione "Arquivo → Selecionar Diretório"
       - O caminho do diretório selecionado será exibido acima da tabela

    2. Iniciar/Parar Monitoramento:
       - Clique no botão "Iniciar/Parar" ou selecione "Arquivo → Iniciar/Parar"
       - Um escaneamento inicial do diretório será realizado com barra de progresso
       - Para interromper o monitoramento, clique novamente no mesmo botão

Interface Principal:
    - Barra de Menu: Acesso a todas as funções do programa
    - Barra Lateral: Botões de ações rápidas
    - Rótulo de Diretório: Exibe o diretório monitorado
    - Rótulo de Resultado: Mostra o status atual da operação
    - Tabela de Dados: Exibe todos os eventos de monitoramento
    - Barra de Progresso: Visível durante operações de longa duração

    Campos padrão da tabela:
    - Tipo de Operação: Adicionado, Excluído, Modificado, Renomeado ou Movido
    - Nome: Nome do arquivo
    - Diretório Anterior: Local original do arquivo (quando aplicável)
    - Diretório Atual: Local atual do arquivo
    - Data de Criação: Data em que o arquivo foi criado
    - Data de Modificação: Data da última modificação
    - Tipo: Tipo/extensão do arquivo

Filtros e Pesquisa:
    1. Filtros Rápidos:
       - No menu "Configurações → Filtros", marque/desmarque tipos de operações
         (Movido, Renomeado, Adicionado, Excluído, Modificado)

    2. Filtros Avançados:
       - Acesse "Configurações → Filtros → Filtros Avançados"
       - Filtro de Operação: Selecione tipos de operações a visualizar
       - Pesquisa: Busca por texto em nome e diretórios
       - Filtro por Extensão: Filtre por tipos específicos de arquivo
       - Filtro de Data: Defina o período para os eventos
       - Use o botão de calendário para seleção de datas
       - "Limpar Filtros" reseta todas as configurações

Visualização de Estatísticas:
    - Acesse pelo botão "Estatísticas" ou "Arquivo → Estatísticas"
    - Gráficos disponíveis:
      * Distribuição de Operações: Proporção de cada tipo de operação
      * Top 10 Tipos de Arquivo: Tipos de arquivo mais comuns
      * Timeline de Operações: Linha do tempo de eventos
      * Mapa de Árvore: Visualização de tamanho por tipos
      * Distribuição por Hora: Horários com mais operações
      * Análise de Pareto: Frequência e percentual acumulado
      * Operações por Dia: Operações agrupadas por data
    - Salvar gráficos: Clique em "Salvar Todos" e selecione destino

Exportação de Dados:
    - Clique em "Salvar Como" ou "Arquivo → Salvar Como"
    - Formatos disponíveis:
      * Excel (.xlsx)
      * CSV (.csv)
      * Texto (.txt)
      * JSON (.json)
      * XML (.xml)
      * Banco de Dados (.db)
    - Para exportações futuras do mesmo conjunto, use "Arquivo → Salvar"

Configuração de Colunas:
    - Acesse "Configurações → Configurar Colunas"
    - Marque/desmarque colunas desejadas na tabela:
      (Tipo de Operação, Nome, Diretório Anterior, Diretório Atual, etc.)
    - Alterações são aplicadas imediatamente
    - Restauração padrão: "Configurações → Configurar Colunas → Resetar Colunas"

Alteração de Idioma:
    - Acesse "Opções → Idioma" e selecione o idioma desejado
    - O programa será reiniciado com o novo idioma após confirmação

Resolução de Problemas:
    1. Monitoramento não inicia:
       - Verifique permissões de acesso ao diretório
       - Certifique-se que não há outro programa monitorando o mesmo diretório
       - Reinicie o aplicativo

    2. Eventos não aparecem:
       - Verifique se o monitoramento está ativo
       - Confira se os filtros não estão ocultando eventos
       - Teste modificando um arquivo manualmente

    3. Alto consumo de recursos:
       - Evite monitorar diretórios de sistema ou com milhares de arquivos
       - Monitore subdiretórios específicos em vez de diretórios raiz

    4. Erros nas estatísticas:
       - Certifique-se que há eventos suficientes para gerar gráficos
       - Verifique se todas as bibliotecas estão corretamente instaladas

Autores:
- Fernando Nillsson Cidade


# **English:**

Project: PANOPTES PATROL
Version: 0.0.9
Authors: Fernando Nillsson Cidade

Description:
This project is a file and folder manager that monitors changes in a specific directory and displays these changes in a graphical interface. It can detect operations such as adding, deleting, modifying, renaming, and moving files and folders. In addition, the project offers functionality to filter, export data, and generate statistics on operations performed.

QUICK USER MANUAL:

How to use:
1. Run the application to start the graphical interface.
2. Select a directory to monitor.
3. Use the buttons and menus to start/stop monitoring, apply filters, export data, and view statistics.

DETAILED USER MANUAL:

System Requirements:
    - Operating System: Windows 10 or higher.

Installation:
    - Install the program's executable file, follow the installer instructions, and run the program.

Initial Setup:
    - The interface will be displayed with an empty monitoring table.
    - The default language will be selected according to the system configuration.
    - Observe the left sidebar to access the main functions.

Directory Monitoring:
    1. Select a Directory:
       - Click on the "Select Directory" button or select "File → Select Directory"
       - The selected directory path will be displayed above the table

    2. Start/Stop Monitoring:
       - Click on the "Start/Stop" button or select "File → Start/Stop"
       - An initial scan of the directory will be performed with a progress bar
       - To stop monitoring, click the same button again

Main Interface:
    - Menu Bar: Access to all program functions
    - Sidebar: Quick action buttons
    - Directory Label: Displays the monitored directory
    - Result Label: Shows the current operation status
    - Data Table: Displays all monitoring events
    - Progress Bar: Visible during long-duration operations

    Default table fields:
    - Operation Type: Added, Deleted, Modified, Renamed, or Moved
    - Name: File name
    - Previous Directory: Original location of the file (when applicable)
    - Current Directory: Current location of the file
    - Creation Date: Date the file was created
    - Modification Date: Date of the last modification
    - Type: File type/extension

Filters and Search:
    1. Quick Filters:
       - In the "Settings → Filters" menu, check/uncheck operation types
         (Moved, Renamed, Added, Deleted, Modified)

    2. Advanced Filters:
       - Access "Settings → Filters → Advanced Filters"
       - Operation Filter: Select types of operations to view
       - Search: Search for text in name and directories
       - Extension Filter: Filter by specific file types
       - Date Filter: Define the period for events
       - Use the calendar button for date selection
       - "Clear Filters" resets all settings

Statistics Visualization:
    - Access via the "Statistics" button or "File → Statistics"
    - Available charts:
      * Operation Distribution: Proportion of each operation type
      * Top 10 File Types: Most common file types
      * Operation Timeline: Timeline of events
      * Tree Map: Size visualization by types
      * Hour Distribution: Hours with most operations
      * Pareto Analysis: Frequency and cumulative percentage
      * Operations by Day: Operations grouped by date
    - Save charts: Click on "Save All" and select destination

Data Export:
    - Click on "Save As" or "File → Save As"
    - Available formats:
      * Excel (.xlsx)
      * CSV (.csv)
      * Text (.txt)
      * JSON (.json)
      * XML (.xml)
      * Database (.db)
    - For future exports of the same set, use "File → Save"

Column Configuration:
    - Access "Settings → Configure Columns"
    - Check/uncheck desired columns in the table:
      (Operation Type, Name, Previous Directory, Current Directory, etc.)
    - Changes are applied immediately
    - Default restoration: "Settings → Configure Columns → Reset Columns"

Language Change:
    - Access "Options → Language" and select the desired language
    - The program will restart with the new language after confirmation

Troubleshooting:
    1. Monitoring does not start:
       - Check directory access permissions
       - Make sure there is no other program monitoring the same directory
       - Restart the application

    2. Events do not appear:
       - Check if monitoring is active
       - Verify that filters are not hiding events
       - Test by manually modifying a file

    3. High resource consumption:
       - Avoid monitoring system directories or directories with thousands of files
       - Monitor specific subdirectories instead of root directories

    4. Errors in statistics:
       - Make sure there are enough events to generate charts
       - Check that all libraries are correctly installed

Authors:
- Fernando Nillsson Cidade
