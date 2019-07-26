## Description
This is a simple python web server without usage of any web frameworks.
It takes advantage of networking sockets to accept TCP connections and forward data between client and servers.
By default web server accepts connections at localhost on port 8080. This can be modified in main.py file.

During testing I was using a simple example of a database represented as a dictionary DATABASE in web_server.py file.
As an additional improvement in future, it might be cool to use a real database instead.

Also it includes a sample REST API from REST API Exercism task here https://exercism.io/my/tracks/python

The code is not complete and requires major refactoring, but it does the job. It only covers the bare minimum
to be able to pass unit tests for the Exercism challenge.

## Usage and supported API calls:

1) in terminal window run python main.py 
2) running unit tests: pytest rest_api_test.py
3) execute API calls using tool of your choice (Postman, curl, etc). Examples with curl from another terminal window:
- curl -XGET localhost:8080/users -d '{"users": ["Adam"]}'
- curl -XPOST localhost:8080/add -d '{"user": "Roman"}'
- curl -XPOST localhost:8080/iou -d '{"lender": "Roman", "borrower": "Chuck", "amount": 15}'    

Thanks to @joncardasis and his example of the web server here https://gist.github.com/joncardasis/cc67cfb160fa61a0457d6951eff2aeae 