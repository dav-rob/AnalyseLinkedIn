DROP VIEW IF EXISTS view1;

CREATE VIEW view1 AS
    SELECT
        job_id,
        job_title,
        company,
        job_details,
        created_date,
        json_extract(analysis, '$.match_score') AS match_score,
        json_extract(analysis, '$.strengths') AS strengths,
        json_extract(analysis, '$.gaps') AS gaps,
        json_extract(analysis, '$.detailed_analysis') AS detailed_analysis,
        footer_info
    FROM jobs
    ORDER BY match_score DESC;