# Akara's shop

> You all remember akara ... right?

Shop backend API with Python 3.6+ and Starlette using Graphql. This project is published in github and can be seen [here](https://github.com/rolurq/shopify-backend-challenge).

## Setup

A `Pipfile` is present in order to use enviroment setup using `pipenv`. Simply run

```sh
$ pipenv install
```

to create and setup a virtual environment.

### Database

This project uses `tinydb` as database provider, given that is a showcase project. This database should not be used in real environments given its performance issues.

All the data relevant for testing is in `data/data.json`, which contains some products and a single user. The user has `admin` as both username and pasword.

## Starting the server

To start the server run:

```sh
$ pipenv run scripts/start.sh
```

This starts the server with debug configuration, to start it in production mode, run:

```sh
$ GUNICORN_CONFIG=python:config.gunicorn_prod pipenv run scripts/start.sh
```

## Running tests

Before running the tests, ensure all development dependencies are installed running:

```sh
$ pipenv install --dev
```

Then, to run all tests:

```sh
$ pipenv run scripts/test.sh
```