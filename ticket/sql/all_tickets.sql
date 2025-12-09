SELECT
    t.t_id as ticket_id,
    t.riad,
    t.seat,
    t.price,
    s.session_id,
    DATE_FORMAT(s.data, '%%d.%%m.%%Y') as session_date,
    s.time,
    t.is_sold,
    m.title as movie_title,
    h.hall_name
FROM ticket t
JOIN Session s ON t.sessionticket_id = s.session_id
JOIN Movies m ON s.moviesession_id = m.m_id
JOIN Hall h ON s.hallsession_id = h.h_id
WHERE s.session_id = %s
AND s.data >= CURDATE()
ORDER BY t.riad, t.seat