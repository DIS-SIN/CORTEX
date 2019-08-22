import { ApolloServer } from "apollo-server-express";
import express from "express";
import { v1 as neo4j } from "neo4j-driver";
import { makeAugmentedSchema, inferSchema } from "neo4j-graphql-js";
import dotenv from "dotenv";

// set environment variables from ../.env
dotenv.config();

const app = express();
var cors = require('cors');
app.use(cors());


/*
 * Create a Neo4j driver instance to connect to the database
 * using credentials specified as environment variables
 * with fallback to defaults
 */
const driver = neo4j.driver(
  process.env.NEO4J_URI || "bolt://localhost:7687",
  neo4j.auth.basic(
    process.env.NEO4J_USER || "neo4j",
    process.env.NEO4J_PASSWORD || "password"
  )
);

const schemaInferenceOptions = {
  alwaysIncludeRelationships: false
};

const customTypeDefs = `
  type Query {
    all_2019_course_data: [Course]
      @cypher(
        statement: "MATCH (c:Course)-[:COURSE_OF]->(o:Offering) WHERE o.start_date CONTAINS '2019' RETURN DISTINCT (c)"
      )
    all_offs_data(from: String, to: String): [Offering]
      @cypher(
        statement: "MATCH (o:Offering) WHERE date(o.start_date) >= date($from) AND date(o.start_date) <= date($to) RETURN o"
      )
    get_course_code(code: String): Course
      @cypher(
        statement: "MATCH (c:Course {code:$code}) RETURN c"
      )
    get_offerings(code: String, from: String, to: String): [Offering]
      @cypher(
        statement: "MATCH (c:Course {code:$code})-[:COURSE_OF]-(o:Offering)  WHERE date(o.start_date) >= date($from) AND date(o.start_date) <= date($to) RETURN o"
      )
  }
`;

const schema = inferSchema(driver, schemaInferenceOptions).then(result => {
  return makeAugmentedSchema({
    typeDefs: result.typeDefs + customTypeDefs
  });
});

/*
 * Create a new ApolloServer instance, serving the GraphQL schema
 * created using makeAugmentedSchema above and injecting the Neo4j driver
 * instance into the context object so it is available in the
 * generated resolvers to connect to the database.
 */
const server = new ApolloServer({
  context: { driver },
  schema: schema,
  introspection: true,
  playground: true
});

// Specify port and path for GraphQL endpoint
const port = process.env.GRAPHQL_LISTEN_PORT || 4000;
const path = "/graphql";

/*
* Optionally, apply Express middleware for authentication, etc
* This also also allows us to specify a path for the GraphQL endpoint
*/
server.applyMiddleware({app, path});

app.listen({port, path}, () => {
  console.log(`GraphQL server ready at http://localhost:${port}${path}`);
});