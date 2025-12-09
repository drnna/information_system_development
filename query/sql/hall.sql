SELECT
    h.h_id,
    h.hall_name,
    h.seats_count,
    COUNT(DISTINCT s.session_id) as total_sessions,
    COUNT(t.t_id) as sold_tickets,
    COALESCE(SUM(t.price), 0) as total_revenue
FROM
    Hall h
LEFT JOIN
    Session s ON h.h_id = s.hallsession_id
LEFT JOIN
    Ticket t ON s.session_id = t.sessionticket_id AND t.is_sold = 1
WHERE
    h.h_id = (%s)
GROUP BY
    h.h_id, h.hall_name, h.seats_count
ORDER BY
    h.hall_name;