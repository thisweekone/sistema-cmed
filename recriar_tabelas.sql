-- Recriar tabela medicamentos
DROP TABLE IF EXISTS medicamentos;
CREATE TABLE medicamentos (
    id SERIAL PRIMARY KEY,
    substancia TEXT,
    cnpj TEXT,
    laboratorio TEXT,
    codigo_ggrem TEXT,
    registro TEXT,
    ean TEXT,
    produto TEXT,
    apresentacao TEXT,
    classe_terapeutica TEXT,
    tipo_produto TEXT,
    regime_preco TEXT,
    pf_sem_imposto DECIMAL,
    pf DECIMAL,
    pmvg_sem_imposto DECIMAL,
    pmvg DECIMAL,
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

-- Recriar tabela precos
DROP TABLE IF EXISTS precos;
CREATE TABLE precos (
    id SERIAL PRIMARY KEY,
    substancia TEXT,
    cnpj TEXT,
    laboratorio TEXT,
    codigo_ggrem TEXT,
    registro TEXT,
    ean TEXT,
    produto TEXT,
    apresentacao TEXT,
    pf_sem_imposto DECIMAL,
    pf DECIMAL,
    pmvg_sem_imposto DECIMAL,
    pmvg DECIMAL,
    data_publicacao DATE
);
