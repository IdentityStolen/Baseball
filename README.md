# Baseball



## Example django command run

Run command inside web container:

`python manage.py load_players`

![img.png](img.png)


## Get players by hits

http://localhost:8000/api/baseball/players/by-hits/


## React Frontend UI

http://localhost:3000/


## Get Decsription using LLM

http://localhost:8000/api/baseball/players/{player_id}/description/

e.g. http://localhost:8000/api/baseball/players/1/description/


Opportunities for Improvement:

1. Pagination: Implement pagination for the player list API to handle large datasets efficiently.
2. unit & integration tests: Add comprehensive tests for both backend and frontend components to ensure reliability.
3. Error Handling: Improve error handling in the frontend to provide better user feedback.
4. Caching: Implement caching for frequently accessed data to improve performance.
5. UI Enhancements: Enhance the frontend UI with better styling and user experience features.
6. Authentication: Add user authentication and authorization for secure access to the API.
