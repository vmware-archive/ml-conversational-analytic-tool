# CIE - Constructiveness and Inclusiveness Evaluator

## Project contributors
It is a group project done by:

@olga-kondr

@yuanqian-usf

@mycarreno

@gcappellani

## Group mentors

@mkbhanda

@annajung


## Build Instructions

### In Docker
To get the project up and running in Docker

1. Clone the repository
2. Make sure that Docker is installed and running
3. In the console run the following command to build the application:

```docker-compose build```

4. In the console run the following command to start the application:

```docker-compose up```

5. When you are done using it and want to shut down just press CTRL + C and close terminal and docker application.

#### When you are done using it and want to remove images run the following command: 
```docker-compose down -v```

### Locally
To get the project up and running locally
1. Clone the repository
2. Make sure that Docker is installed and running as DB is configured to Docker
3. Run DB in Docker
4. Under /back/flask/extract/graph_ql_request.py, replace {YOUR_ACCESS_TOEKN} with your own access_token
5. Create a virtual environment:

```python3 -m venv .venv```
```source .venv/bin/activate```

6. After the environment created, in the console open ‘back’ folder by 
 
 ```cd <cloned folder path>/back``` 

and run the following commands to install requirements:

```pip install -r requirements.txt```

7. Now open second console window and go to the ml folder 

```cd <cloned folder path>/ml```

8. Run the following commands to install requirements:

```pip install -r requirements.txt```

9. After all required packages installed, in the console run the following commands to start the ml application:

```export FLASK_APP=service```

```flask run --host 0.0.0.0 --port 5001```

11. Make sure it is up and running by visiting localhost:5001/health in the browser, if it shows response then close this page, no need to keep it open.
12. Switch to the first console and run the following commands to start the main application:

```export FLASK_APP=flaskr```

```flask run```

13. If everything went well by opening localhost:5000/ in the browser you see the welcome page.

#### When you are done using the application and want to shut it down:

1. Open both console windows and just press CTRL + C in both consoles.
2. In any console close the virtual environment by:
deactivate
3. To close DB image run the following command:
docker-compose down
