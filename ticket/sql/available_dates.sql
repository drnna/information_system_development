SELECT DISTINCT s.data as session_date
FROM Session s
JOIN ticket t ON s.session_id = t.sessionticket_id
WHERE s.data >= CURDATE()
AND t.is_sold = 0
ORDER BY s.data