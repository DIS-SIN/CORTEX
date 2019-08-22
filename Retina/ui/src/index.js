import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './components/App/App'
import * as serviceWorker from './serviceWorker';
import 'bootstrap/dist/css/bootstrap.css';
import ApolloClient from "apollo-boost";
import { ApolloProvider } from "react-apollo";

const client = new ApolloClient({
    uri: process.env.REACT_APP_GRAPHQL_URI
});

const Main = () => (
    <ApolloProvider client={client}>
      <App />
    </ApolloProvider>
);

ReactDOM.render(<Main />, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
