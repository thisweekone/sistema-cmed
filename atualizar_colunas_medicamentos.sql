-- Backup dos dados existentes
CREATE TABLE medicamentos_backup AS SELECT * FROM medicamentos;

-- Remover tabela existente
DROP TABLE IF EXISTS medicamentos CASCADE;

-- Criar nova tabela com todas as colunas
CREATE TABLE medicamentos (
    id SERIAL PRIMARY KEY,
    substancia TEXT,
    cnpj TEXT,
    laboratorio TEXT,
    codigo_ggrem TEXT,
    registro TEXT,
    ean_1 TEXT,
    ean_2 TEXT,
    ean_3 TEXT,
    produto TEXT,
    apresentacao TEXT,
    classe_terapeutica TEXT,
    tipo_produto TEXT,
    regime_preco TEXT,
    pf_sem_impostos DECIMAL,
    pf_0 DECIMAL,
    pf_12 DECIMAL,
    pf_12_alc DECIMAL,
    pf_17 DECIMAL,
    pf_17_alc DECIMAL,
    pf_17_5 DECIMAL,
    pf_17_5_alc DECIMAL,
    pf_18 DECIMAL,
    pf_18_alc DECIMAL,
    pf_19 DECIMAL,
    pf_19_alc DECIMAL,
    pf_19_5 DECIMAL,
    pf_19_5_alc DECIMAL,
    pf_20 DECIMAL,
    pf_20_alc DECIMAL,
    pf_20_5 DECIMAL,
    pf_21 DECIMAL,
    pf_21_alc DECIMAL,
    pf_22 DECIMAL,
    pf_22_alc DECIMAL,
    pmc_sem_imposto DECIMAL,
    pmc_0 DECIMAL,
    pmc_12 DECIMAL,
    pmc_12_alc DECIMAL,
    pmc_17 DECIMAL,
    pmc_17_alc DECIMAL,
    pmc_17_5 DECIMAL,
    pmc_17_5_alc DECIMAL,
    pmc_18 DECIMAL,
    pmc_18_alc DECIMAL,
    pmc_19 DECIMAL,
    pmc_19_alc DECIMAL,
    pmc_19_5 DECIMAL,
    pmc_19_5_alc DECIMAL,
    pmc_20 DECIMAL,
    pmc_20_alc DECIMAL,
    pmc_20_5 DECIMAL,
    pmc_21 DECIMAL,
    pmc_21_alc DECIMAL,
    pmc_22 DECIMAL,
    pmc_22_alc DECIMAL,
    restricao_hospitalar BOOLEAN,
    cap BOOLEAN,
    confaz_87 BOOLEAN,
    icms_0 BOOLEAN,
    analise_recursal BOOLEAN,
    lista_concessao_credito BOOLEAN,
    comercializacao_2022 BOOLEAN,
    tarja TEXT,
    data_publicacao DATE
);

-- Restaurar dados do backup
INSERT INTO medicamentos (
    id, substancia, cnpj, laboratorio, codigo_ggrem, registro,
    produto, apresentacao, classe_terapeutica, tipo_produto,
    regime_preco, restricao_hospitalar, cap, confaz_87, icms_0,
    analise_recursal, lista_concessao_credito, comercializacao_2022,
    tarja, data_publicacao
)
SELECT 
    id, substancia, cnpj, laboratorio, codigo_ggrem, registro,
    produto, apresentacao, classe_terapeutica, tipo_produto,
    regime_preco, restricao_hospitalar, cap, confaz_87, icms_0,
    analise_recursal, lista_concessao_credito, comercializacao_2022,
    tarja, data_publicacao
FROM medicamentos_backup;

-- Remover tabela de backup
DROP TABLE medicamentos_backup;

-- Permitir acesso via API REST
ALTER TABLE medicamentos ENABLE ROW LEVEL SECURITY;

-- Criar políticas de acesso
CREATE POLICY "Enable read access for all users" ON medicamentos
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for authenticated users" ON medicamentos
    FOR INSERT WITH CHECK (true);
