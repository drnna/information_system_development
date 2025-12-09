SELECT
    s.session_id,
    s.data as session_date,
    s.time as session_time,
    m.title as movie_title,
    h.hall_name,
    h.seats_count
FROM
    session s
JOIN
    movies m ON s.moviesession_id = m.m_id
JOIN
    hall h ON s.hallsession_id = h.h_id
LEFT JOIN
    ticket t ON s.session_id = t.sessionticket_id AND t.is_sold = 1
WHERE
    YEAR(s.data) = %s
    AND t.t_id IS NULL
ORDER BY
    s.data, s.time;