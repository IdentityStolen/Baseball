React frontend that fetches players from the Django API at /api/baseball/players/by-hits/

To run locally without Docker:

1. cd frontend
2. npm install
3. REACT_APP_API_URL="http://localhost:8000/api/baseball/players/by-hits/" npm start

To run with Docker compose (after starting Django `web` service):

docker-compose up --build frontend

The frontend service depends on `web` service in docker-compose and uses `http://web:8000/api/baseball/players/by-hits/` by default inside containers.

