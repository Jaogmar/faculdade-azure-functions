CREATE OR ALTER VIEW dbo.vw_ind_total_chamados AS
SELECT COUNT(*) AS total_chamados FROM dbo.chamado;
GO
CREATE OR ALTER VIEW dbo.vw_ind_chamados_por_analista AS
SELECT a.nm_analista, COUNT(c.id_chamado) AS total_chamados
FROM dbo.analista a LEFT JOIN dbo.chamado c ON c.id_analista_atual = a.id_analista
GROUP BY a.nm_analista;
GO
CREATE OR ALTER VIEW dbo.vw_ind_chamados_abertos_por_mes AS
SELECT FORMAT(dt_criacao, 'yyyy-MM') AS mes, COUNT(*) AS chamados_abertos
FROM dbo.chamado GROUP BY FORMAT(dt_criacao, 'yyyy-MM');
GO
CREATE OR ALTER VIEW dbo.vw_ind_chamados_por_status AS
SELECT ds_status_chamado, COUNT(*) AS total FROM dbo.chamado GROUP BY ds_status_chamado;
GO
CREATE OR ALTER VIEW dbo.vw_ind_sla_cumprimento AS
SELECT s.nm_sla, COUNT(*) AS total,
       SUM(CASE WHEN cs.fl_breach = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS pct_dentro_sla
FROM dbo.chamado_sla cs JOIN dbo.sla s ON s.id_sla = cs.id_sla GROUP BY s.nm_sla;
GO
CREATE OR ALTER VIEW dbo.vw_ind_csat_medio AS
SELECT AVG(CAST(nr_score AS float)) AS csat_medio, COUNT(*) AS avaliacoes FROM dbo.csat_avaliacao;
GO
CREATE OR ALTER VIEW dbo.vw_ind_tempo_medio_resolucao AS
SELECT AVG(DATEDIFF(MINUTE, dt_criacao, dt_resolucao)) AS minutos_medio_resolucao
FROM dbo.chamado WHERE dt_resolucao IS NOT NULL;
GO
