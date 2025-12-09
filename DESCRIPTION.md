```Hall```<br>

| h_id | hall_name | seats_count |
|------|-----------|-------------|
| INT  | VARCHAR   | INT         |

```Movies```<br>

| m_id | title  | country | year  | direction | film_studio | lenght |
|------|--------|---------|-------|-----------|-------------|--------|
| INT  | VARCHAR | VARCHAR | INT | VARCHAR    |VARCHAR    |INT |

```internal_users```<br>

| u_id | login | password | user_group   |
|------| ---- |----------|--------------|
| INT  | VARCHAR | VARCHAR  | VARCHAR      |

```order_list```<br>

| ol_id | uo_id | session_id | ticket_amount | total_price |
|-------|-------|------------|---------------|-------------|
| INT   | INT   | INT        | INT           | DECIMAL     |

```Position_sheme```<br>

| position_id | riad | first_point | last_point | base_price | hallposition_id |
|-------------|------|-------------|------------|------------|------------|
| INT         | INT  | INT         | INT        | DECIMAL      |INT        |

```revenue_report```<br>

| rr_id | revenue | ses_amount | ticket_amount | sr_year | sr_month |
|-------|---------|------------|------------|-------|-------|
| INT   | DECIMAL     | INT       | INT        |INT        |INT        |

```Session```<br>

| session_id | data | coefficient | moviesession_id | hallsession_id | time |
|------------|------|-------------|-------------|-------------|-------------|
| INT        | DATE  | DECIMAL       |INT        |INT        |VARCHAR      |

```session_report```<br>

| sr_id | hall_name | sr_month | sr_year | sr_amount | sr_value |
|-------|-----------|----------|---------|-----------|----------|
| INT   | VARCHAR   | INT      | INT     | INT       | DECIMAL  |

```ticket```<br>

| t_id | riad | seat | price   | is_sold | sessionticket_id |
|------|------|------|---------|---------|------------------|
| INT  | INT  | INT  | DECIMAL | TINYINT | INT              |

```user_order```<br>

| uo_id | u_id | order_date | 
|-------|------|------------|
| INT   | INT  | DATETIME   | 




    




