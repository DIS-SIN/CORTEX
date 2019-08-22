import React from "react";
import { Query } from "react-apollo";
import gql from "graphql-tag";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow
} from "@material-ui/core";

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
                course_of{
                registered_for{
                    uid
                },
                surveyed_for{
                    uid
                }
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

            let reg_count = 0;
            let resp_count = 0;

            for(let off of data.get_course_code.course_of){
                reg_count += off.registered_for.length;
                resp_count += off.surveyed_for.length;
            }

            return (
                <div class="row">
                    <div class="col-sm-6">
                        <Table>
                            <TableHead>
                            <TableRow>
                                <TableCell>Learners</TableCell>
                                <TableCell>Responses</TableCell>
                                <TableCell>Rate</TableCell>
                            </TableRow>
                            </TableHead>
                            <TableBody>
                                <TableCell>{reg_count}</TableCell>
                                <TableCell>{resp_count}</TableCell>
                                <TableCell>{((resp_count / reg_count) * 100).toFixed(2)}</TableCell>
                            </TableBody>
                        </Table>
                    </div>
                </div>              
            );
        }}
      </Query>
    );
  }
}

export default CourseTypes;