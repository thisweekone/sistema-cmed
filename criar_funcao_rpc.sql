-- Criar função para executar comandos SQL dinamicamente
CREATE OR REPLACE FUNCTION atualizar_estrutura(sql_command text)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    EXECUTE sql_command;
END;
$$;
