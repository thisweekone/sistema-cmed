-- Função para importar medicamentos em massa
CREATE OR REPLACE FUNCTION public.importar_medicamentos_em_massa(registros JSONB)
RETURNS integer AS $$
DECLARE
  total_registros INTEGER := 0;
  registro JSONB;
BEGIN
  -- Inserir cada registro na tabela
  FOR registro IN SELECT * FROM jsonb_array_elements(registros)
  LOOP
    INSERT INTO public.medicamentos (
      substancia, cnpj, laboratorio, codigo_ggrem, registro, 
      ean_1, ean_2, ean_3, produto, apresentacao, 
      classe_terapeutica, tipo_de_produto, regime_de_preco,
      restricao_hospitalar, cap, confaz_87, icms_0, 
      analise_recursal, lista_concessao_credito, comercializacao_2022,
      tarja, pf_sem_impostos, pf_0, pf_12, pf_12_alc, 
      pf_17, pf_17_alc, pf_17_5, pf_17_5_alc, pf_18, 
      pf_18_alc, pf_19, pf_19_alc, pf_19_5, pf_19_5_alc, 
      pf_20, pf_20_alc, pf_20_5, pf_21, pf_21_alc, 
      pf_22, pf_22_alc, pmc_sem_imposto, pmc_0, pmc_12, 
      pmc_12_alc, pmc_17, pmc_17_alc, pmc_17_5, pmc_17_5_alc, 
      pmc_18, pmc_18_alc, pmc_19, pmc_19_alc, pmc_19_5, 
      pmc_19_5_alc, pmc_20, pmc_20_alc, pmc_20_5, pmc_21, 
      pmc_21_alc, pmc_22, pmc_22_alc, data_publicacao
    )
    VALUES (
      (registro->>'substancia')::TEXT,
      (registro->>'cnpj')::TEXT,
      (registro->>'laboratorio')::TEXT,
      (registro->>'codigo_ggrem')::TEXT,
      (registro->>'registro')::TEXT,
      (registro->>'ean_1')::TEXT,
      (registro->>'ean_2')::TEXT,
      (registro->>'ean_3')::TEXT,
      (registro->>'produto')::TEXT,
      (registro->>'apresentacao')::TEXT,
      (registro->>'classe_terapeutica')::TEXT,
      COALESCE((registro->>'tipo_de_produto')::TEXT, (registro->>'tipo_produto')::TEXT),
      COALESCE((registro->>'regime_de_preco')::TEXT, (registro->>'regime_preco')::TEXT),
      (registro->>'restricao_hospitalar')::BOOLEAN,
      (registro->>'cap')::BOOLEAN,
      (registro->>'confaz_87')::BOOLEAN,
      (registro->>'icms_0')::BOOLEAN,
      (registro->>'analise_recursal')::BOOLEAN,
      (registro->>'lista_concessao_credito')::BOOLEAN,
      (registro->>'comercializacao_2022')::BOOLEAN,
      (registro->>'tarja')::TEXT,
      (registro->>'pf_sem_impostos')::DECIMAL,
      (registro->>'pf_0')::DECIMAL,
      (registro->>'pf_12')::DECIMAL,
      (registro->>'pf_12_alc')::DECIMAL,
      (registro->>'pf_17')::DECIMAL,
      (registro->>'pf_17_alc')::DECIMAL,
      (registro->>'pf_17_5')::DECIMAL,
      (registro->>'pf_17_5_alc')::DECIMAL,
      (registro->>'pf_18')::DECIMAL,
      (registro->>'pf_18_alc')::DECIMAL,
      (registro->>'pf_19')::DECIMAL,
      (registro->>'pf_19_alc')::DECIMAL,
      (registro->>'pf_19_5')::DECIMAL,
      (registro->>'pf_19_5_alc')::DECIMAL,
      (registro->>'pf_20')::DECIMAL,
      (registro->>'pf_20_alc')::DECIMAL,
      (registro->>'pf_20_5')::DECIMAL,
      (registro->>'pf_21')::DECIMAL,
      (registro->>'pf_21_alc')::DECIMAL,
      (registro->>'pf_22')::DECIMAL,
      (registro->>'pf_22_alc')::DECIMAL,
      (registro->>'pmc_sem_imposto')::DECIMAL,
      (registro->>'pmc_0')::DECIMAL,
      (registro->>'pmc_12')::DECIMAL,
      (registro->>'pmc_12_alc')::DECIMAL,
      (registro->>'pmc_17')::DECIMAL,
      (registro->>'pmc_17_alc')::DECIMAL,
      (registro->>'pmc_17_5')::DECIMAL,
      (registro->>'pmc_17_5_alc')::DECIMAL,
      (registro->>'pmc_18')::DECIMAL,
      (registro->>'pmc_18_alc')::DECIMAL,
      (registro->>'pmc_19')::DECIMAL,
      (registro->>'pmc_19_alc')::DECIMAL,
      (registro->>'pmc_19_5')::DECIMAL,
      (registro->>'pmc_19_5_alc')::DECIMAL,
      (registro->>'pmc_20')::DECIMAL,
      (registro->>'pmc_20_alc')::DECIMAL,
      (registro->>'pmc_20_5')::DECIMAL,
      (registro->>'pmc_21')::DECIMAL,
      (registro->>'pmc_21_alc')::DECIMAL,
      (registro->>'pmc_22')::DECIMAL,
      (registro->>'pmc_22_alc')::DECIMAL,
      (registro->>'data_publicacao')::DATE
    );
    
    total_registros := total_registros + 1;
  END LOOP;
  
  RETURN total_registros;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para obter contagem real de medicamentos
CREATE OR REPLACE FUNCTION public.contar_medicamentos()
RETURNS integer AS $$
DECLARE
  total_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO total_count FROM public.medicamentos;
  RETURN total_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
