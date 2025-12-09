SELECT
    s.session_id,
    s.time,
    m.title as movie_title,
    h.hall_name,
    COUNT(CASE WHEN t.is_sold = 0 THEN 1 END) as available_tickets,
    h.seats_count as total_seats
FROM Session s
JOIN Movies m ON s.moviesession_id = m.m_id
JOIN Hall h ON s.hallsession_id = h.h_id
JOIN ticket t ON s.session_id = t.sessionticket_id
WHERE s.data = %s
AND s.data >= CURDATE()
GROUP BY s.session_id, s.time, m.title, h.hall_name, h.seats_count
HAVING available_tickets > 0
ORDER BY s.time