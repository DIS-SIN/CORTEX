# Retina
Retina is a dashboard tool used to visualize data exported loaded [Gungnir](https://github.com/dis-sin/gungnir).


## Usage
- [Getting Started](#getting-started)
- [Deployment](#deployment)
- [Built with](#built-with)

## Getting Started

These instructions will get you a copy of the visualizer up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Retina is built with nodeJS packages, therefore will require nodeJS to be installed. It also uses [Gungnir](https://github.com/dis-sin/gungnir), therefore will require an instance of Gungnir running somewhere. 

You will also need to create an .env file which will contain your [Gungnir](https://github.com/dis-sin/gungnir) URI endpoint. It should look like these (Depending on your setup):

```
REACT_APP_GRAPHQL_URI=http://{YOUR _GUNGNIR_IP}:{YOUR_GUNGNIR_PORT}/graphql
```

### Installing

Once nodeJS is installed, we are ready to get started. 

These steps will help you get started: 

1. Clone or fork the repo
2. Install the dependencies:

    ```cmd
    cd Retina/ui
    npm install
    ```

## Deployment

You can deploy the tool using docker.

## Built with

- React
- Recharts
