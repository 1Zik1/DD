-- Удаляем старые представления
DROP VIEW IF EXISTS teacher_experience;
DROP VIEW IF EXISTS teaching_quality;
DROP VIEW IF EXISTS teacher_portfolio;

-- Создаем новое представление teacher_experience
CREATE VIEW teacher_experience AS
SELECT 
    t.id AS teacher_id,
    t.last_name || ' ' || t.first_name AS fio,
    SUM(EXTRACT(YEAR FROM age(COALESCE(e.end_date, CURRENT_DATE), e.start_date))) 
        FILTER (WHERE e.experience_type = 'General') AS general_experience,
    SUM(EXTRACT(YEAR FROM age(COALESCE(e.end_date, CURRENT_DATE), e.start_date))) 
        FILTER (WHERE e.experience_type = 'Education') AS education_experience,
    SUM(EXTRACT(YEAR FROM age(COALESCE(e.end_date, CURRENT_DATE), e.start_date))) 
        FILTER (WHERE e.experience_type = 'College') AS college_experience
FROM teachers t
LEFT JOIN experience e ON t.id = e.teacher_id
GROUP BY t.id;

-- Создаем новое представление teaching_quality
CREATE VIEW teaching_quality AS
SELECT
    t.id AS teacher_id,
    t.last_name || ' ' || t.first_name AS fio,
    d.name AS discipline,
    g.number AS group_number,
    tl.year,
    tl.semester,
    ROUND(AVG(gr.grade), 2) AS average_grade,
    COUNT(gr.id) AS grade_count,
    COUNT(CASE WHEN gr.grade = 5 THEN 1 END) * 100.0 / COUNT(gr.id) AS percent_excellent
FROM teachers t
JOIN teaching_load tl ON t.id = tl.teacher_id
JOIN disciplines d ON tl.discipline_id = d.id
JOIN groups g ON tl.group_id = g.id
JOIN grades gr ON gr.discipline_id = d.id AND gr.teacher_id = t.id
GROUP BY t.id, d.name, g.number, tl.year, tl.semester;

-- Создаем новое представление teacher_portfolio
CREATE VIEW teacher_portfolio AS
SELECT
    t.id AS teacher_id,
    t.last_name || ' ' || t.first_name AS fio,
    (SELECT COUNT(*) FROM education WHERE teacher_id = t.id) AS education_count,
    (SELECT SUM(EXTRACT(YEAR FROM age(COALESCE(end_date, CURRENT_DATE), start_date)))
     FROM experience WHERE teacher_id = t.id AND experience_type = 'General') AS general_experience_years,
    (SELECT STRING_AGG(DISTINCT d.name, ', ')
     FROM teaching_load tl
     JOIN disciplines d ON tl.discipline_id = d.id
     WHERE tl.teacher_id = t.id) AS taught_disciplines,
    (SELECT ROUND(AVG(grade), 2)
     FROM grades
     WHERE teacher_id = t.id) AS student_average_grade,
    (SELECT COUNT(*) FROM diplomas WHERE supervisor_id = t.id) AS diploma_count,
    (SELECT COUNT(*) FROM publications WHERE teacher_id = t.id) AS publication_count,
    (SELECT COUNT(*) FROM awards WHERE teacher_id = t.id) AS award_count,
    (SELECT COUNT(*) FROM olympiads
     WHERE teacher_id = t.id AND place = 1 AND level IN ('Regional','National')) AS winner_count
FROM teachers t;