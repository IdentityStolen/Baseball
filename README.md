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
