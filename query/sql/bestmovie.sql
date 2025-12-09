WITH session_tickets AS (
    SELECT
        s.session_id,
        COUNT(t.t_id) as tickets_sold
    FROM
        Session s
    JOIN
        Ticket t ON s.session_id = t.sessionticket_id
    WHERE
        YEAR(s.data) = %s
    GROUP BY
        s.session_id
),
max_tickets AS (
    SELECT MAX(tickets_sold) as max_count
    FROM session_tickets
)
SELECT
    s.session_id,
    s.data,
    s.time,
    h.hall_name,
    m.title,
    m.direction,
    st.tickets_sold
FROM
    Session s
JOIN
    session_tickets st ON s.session_id = st.session_id
JOIN
    max_tickets mt ON st.tickets_sold = mt.max_count
JOIN
    Hall h ON s.hallsession_id = h.h_id
JOIN
    movies m ON s.moviesession_id = m.m_id
ORDER BY
    s.data, s.time;