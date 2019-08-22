import React from "react";
import { Query } from "react-apollo";
import gql from "graphql-tag";
import { withStyles } from "@material-ui/core/styles";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tooltip,
  TableSortLabel
} from "@material-ui/core";
import Extra from './Extra';

class CourseTypes extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      order: "asc",
      orderBy: "code",
      page: 0,
      rowsPerPage: 500
    };
  }

  handleSortRequest = property => {
    const orderBy = property;
    let order = "desc";

    if (this.state.orderBy === property && this.state.order === "desc") {
      order = "asc";
    }

    this.setState({ order, orderBy });
  };

  render() {
    const { order, orderBy } = this.state;
    return (
      <Query
        query={gql`query offeringsRangeQuery(
            $code: String
        ){
            get_course_code(code:$code){
                title,
                deliverytypes{
                    name
                },
                businesstypes{
                    name
                }
            }
        }
    `}
    variables={{
        code: this.props.code
    }}>
        {({ loading, error, data }) => {
          if (loading) return <p class="d-flex justify-content-center mt-5">Loading...</p>;
          if (error) return <p class="d-flex justify-content-center mt-5">Error</p>;
          if (!data.get_course_code) return <p class="d-flex justify-content-center mt-5">Empty set!</p>;
          return (
              <div>
                <h1>{data.get_course_code.title}</h1>
                <div class="row">
                  <div class="col-lg-4">
                      <Table>
                          <TableHead>
                          <TableRow>
                              <TableCell
                              key="name"
                              sortDirection={orderBy === "name" ? order : false}
                              >
                              <Tooltip
                                  title="Sort"
                                  placement="bottom-start"
                                  enterDelay={300}
                              >
                                  <TableSortLabel
                                  active={orderBy === "name"}
                                  direction={order}
                                  onClick={() => this.handleSortRequest("name")}
                                  >
                                  Delivery types
                                  </TableSortLabel>
                              </Tooltip>
                              </TableCell>
                          </TableRow>
                          </TableHead>
                          <TableBody>
                          {data.get_course_code.deliverytypes.map(n => {
                              return (
                              <TableRow key={n._id}>
                                  <TableCell>{n.name}</TableCell>
                              </TableRow>
                              );
                          })}
                          </TableBody>
                      </Table>
                  </div>

                  <div class="col-lg-4">
                      <Table>
                          <TableHead>
                          <TableRow>
                              <TableCell
                              key="name"
                              sortDirection={orderBy === "name" ? order : false}
                              >
                              <Tooltip
                                  title="Sort"
                                  placement="bottom-start"
                                  enterDelay={300}
                              >
                                  <TableSortLabel
                                  active={orderBy === "name"}
                                  direction={order}
                                  onClick={() => this.handleSortRequest("name")}
                                  >
                                  Business types
                                  </TableSortLabel>
                              </Tooltip>
                              </TableCell>
                          </TableRow>
                          </TableHead>
                          <TableBody>
                          {data.get_course_code.businesstypes.map(n => {
                              return (
                              <TableRow key={n._id}>
                                  <TableCell>{n.name}</TableCell>
                              </TableRow>
                              );
                          })}
                          </TableBody>
                      </Table>
                  </div>

                  <div class="col-lg-4">
                    <Extra code={this.props.code} />
                  </div>
                </div> 
              </div>             
          );
        }}
      </Query>
    );
  }
}

export default CourseTypes;