# Activity #5: Pagination and Filtering of Tables via FastAPI + Flet

## Objective

This activity extends the Renewable Energy project with server-side pagination, live search and safe column sorting. The FastAPI backend accepts query parameters, reads from SQLite3 and returns only the requested page. The Flet client rebuilds the table and pager controls whenever the user searches, sorts or changes pages.

## Backend Endpoint

```text
GET /solar/records
```

Supported query parameters:

| Parameter | Purpose |
| --- | --- |
| `user_id` | Owner of the solar records |
| `limit` | Maximum rows returned in one response |
| `offset` | Number of matching rows skipped before returning data |
| `search` | Text filter across record id, panel id, status, type, orientation and timestamp |
| `sort_by` | Whitelisted column used for ordering |
| `order` | Sort direction: `asc` or `desc` |

Example:

```text
http://127.0.0.1:8000/solar/records?user_id=demo_user&limit=10&offset=20&search=active&sort_by=efficiency&order=desc
```

## Pagination Formula

```text
offset = (current_page - 1) * page_size
```

Example: page 3 with 10 rows per page gives `offset = 20`, so the server returns rows 21-30.

## Security

The backend uses a whitelist for `sort_by`. Query parameter values are never allowed to become arbitrary SQL column names.

Allowed sort columns:

- `id`
- `panel_id`
- `power_output`
- `efficiency`
- `temperature`
- `irradiance`
- `status`
- `timestamp`
- `panel_type`
- `orientation`

## Flet Client Features

- Live search field
- Sort dropdown
- Ascending/descending order dropdown
- Rows per page selector
- Previous/Next controls
- Dynamic page number buttons
- Jump to page field
- Record counter
- KPI cards
- CSV export for the current page
- Add record form connected to FastAPI

## Test Checklist

- Run `python comprehensive_api_server.py`
- Open `http://127.0.0.1:8000/docs`
- Run `python seed_activity5.py`
- Run `python lab9_client.py`
- Confirm the table initially shows 10 rows
- Click page 3 and confirm the counter changes
- Type a search term and confirm the pager resets to page 1
- Sort by efficiency descending and confirm table order changes
- Try `sort_by=malicious` in Swagger and confirm the server still responds safely
- Export the current page and confirm a CSV file is created locally
