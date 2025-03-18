-- Adicionar coluna data_publicacao à tabela medicamentos
ALTER TABLE medicamentos 
ADD COLUMN IF NOT EXISTS data_publicacao DATE;

-- Adicionar coluna data_publicacao à tabela precos
ALTER TABLE precos 
ADD COLUMN IF NOT EXISTS data_publicacao DATE;
