# Network Intrusion Detection with Machine Learning

Trabalho de Conclusão de Curso (TCC) de classificação de tráfego de rede: binário (benigno/malicioso) e multiclasse (categorias de ataques). A interface Streamlit recebe atributos numéricos em CSV; não analisa executáveis nem faz engenharia reversa de binários.

## Estado da revisão

O código foi revisado para ajustar imputação e padronização dentro de cada treino e fold de validação, preservar os mapas de classes do XGBoost e exportar pipelines completas. **As métricas antigas não representam esta versão.** As saídas dos notebooks foram limpas e precisam ser recalculadas com os datasets completos.

O antigo download de modelos não é compatível com o contrato atual. A aplicação aceita apenas artefatos locais de versão 2 gerados pelo notebook corrigido. Não há modelo retreinado distribuído neste checkout.

## Instalação e aplicação

Python 3.12 ou superior:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run scripts/app.py
```

Abra http://localhost:8501. Sem modelos, a interface explica o que falta e interrompe a inferência de forma controlada.

## Dados e reprodução

Os notebooks usam os conjuntos IDS2017 e IDS2018 mencionados no trabalho original. Os dados completos não estão versionados. A revisão não baixou nem validou novamente a procedência desses arquivos.

Execute os notebooks na ordem 1 a 4, com o kernel da `.venv`:

1. `1-data-preprocessing.ipynb`: CSVs originais de 2017 em `dados/brutos/IDS2017/`. Para 2018, mantenha também `dados/brutos/IDS2018/` e os três agregados originais `IDS-2018-1-COMPLETO.csv`, `IDS-2018-2-COMPLETO.csv` e `IDS-2018-3-COMPLETO.csv` em `dados/brutos/`. A composição desses grupos não está registrada no código original; esta revisão não inventa uma nova divisão.
2. `2-exploratory-data-analysis.ipynb`: análise dos arquivos em `dados/processados/`.
3. `3-feature-engineering.ipynb`: exportação para `dados/feature/`, incluindo os DataFrames de 2018 com colunas constantes removidas.
4. `4-ml-models.ipynb`: separação estratificada, pipelines com imputação/padronização ajustadas no treino, validação cruzada e avaliação. Exporta `models/modelos.pkl`.

O artefato contém as cinco pipelines de 2017, ordem das features, mapa de classes para XGBoost e versões do ambiente, sem incorporar datasets completos. Os experimentos de 2018 permanecem nos notebooks. Reinicie o kernel antes da nova execução completa.

## Uso dos CSVs

Selecione a tarefa e o modelo explicitamente. A coluna opcional `Tipos de Ataques` é descartada antes da inferência. O aplicativo exige as mesmas features do treino, ordena as colunas e rejeita ausentes, extras e valores não numéricos. Nulos e infinitos passam pela imputação aprendida no treino.

As seis amostras em `amostras/` são apenas exemplos de formato; podem incluir registros usados no estudo e não são um conjunto independente para medir generalização. Os números de classe do XGBoost são convertidos de volta aos nomes originais.

Para gerar outra amostra, sem sobrescrever arquivos existentes:

```powershell
.\.venv\Scripts\python.exe scripts/arquivos.py dados/feature/IDS-2017-FEATURE.csv --output amostras/nova.csv --rows 100
```

## Validação técnica

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes de integração usam amostras pequenas e modelos temporários. Não substituem o treinamento completo nem geram métricas de portfólio.

## Limitações metodológicas

- A amostragem balanceada muda a prevalência do problema; resultados não representam automaticamente tráfego real.
- A seleção multiclasse mantém os limites do estudo (2017: mais de 1.950 registros por classe; 2018: mais de 800; até 9.000 por classe).
- A divisão aleatória não mede generalização temporal nem para outra rede.
- A exclusão de colunas constantes é exploratória e ocorre antes do split; uma avaliação final independente deve também revisar essa seleção.
- As medianas de imputação e os parâmetros de escala são aprendidos apenas dentro das pipelines, inclusive na validação cruzada.
- Não há novas métricas de produção nesta revisão.

## Documentação acadêmica

O PDF `Resumo Executivo - Engenharia Reversa de Malware.pdf` foi preservado como documento histórico, com seu título original. O nome do repositório descreve a implementação de detecção de intrusões em tráfego de rede.

## Licença

Veja [LICENSE](LICENSE). As condições dos datasets e de materiais de terceiros permanecem próprias.
