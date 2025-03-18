-- Criar tabela de medicamentos
CREATE TABLE medicamentos (
    id TEXT PRIMARY KEY,
    substancia TEXT,
    produto TEXT NOT NULL,
    apresentacao TEXT NOT NULL,
    laboratorio TEXT NOT NULL,
    classe_terapeutica TEXT,
    tipo_produto TEXT,
    regime_preco TEXT,
    tarja TEXT,
    lista_concessao TEXT
);

-- Criar tabela de preços
CREATE TABLE precos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    medicamento_id TEXT NOT NULL REFERENCES medicamentos(id),
    ano INTEGER NOT NULL,
    mes INTEGER,
    estado TEXT NOT NULL,
    pf_sem_impostos NUMERIC,
    pf_com_impostos NUMERIC,
    pmc_sem_impostos NUMERIC,
    pmc_com_impostos NUMERIC,
    restricao_hospitalar BOOLEAN DEFAULT FALSE,
    cap BOOLEAN DEFAULT FALSE,
    confaz87 BOOLEAN DEFAULT FALSE,
    icms_0 BOOLEAN DEFAULT FALSE
);

-- Criar índice composto para evitar duplicatas
CREATE UNIQUE INDEX idx_precos_unique ON precos (medicamento_id, ano, mes, estado);

-- Políticas de acesso (opcional)
-- Permitir leitura pública para todos
ALTER TABLE medicamentos ENABLE ROW LEVEL SECURITY;
CREATE POLICY medicamentos_select_policy ON medicamentos FOR SELECT USING (true);

ALTER TABLE precos ENABLE ROW LEVEL SECURITY;
CREATE POLICY precos_select_policy ON precos FOR SELECT USING (true);
