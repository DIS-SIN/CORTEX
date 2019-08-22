import React from "react";
import { Query } from "react-apollo";
import gql from "graphql-tag";
import {
    ResponsiveContainer, ComposedChart, Line, Area, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  } from 'recharts';

class Instructor extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      order: "asc",
      orderBy: "code",
      page: 0,
      rowsPerPage: 500
    };
  }

  render() {
    return (
      <Query
        query={gql`query instructorQuery(
            $code: String
            $from: String
            $to: String
        ){
          get_offerings(code:$code, from:$from, to:$to){
            instructors{
              name
            }
          }
        }
    `}
    variables={{
        code: this.props.code,
        from: this.props.from,
        to: this.props.to
    }}>
        {({ loading, error, data }) => {
          if (loading) return <p class="d-flex justify-content-center mt-5">Loading...</p>;
          if (error) return <p class="d-flex justify-content-center mt-5">Error</p>; if (!data.get_offerings) return <p class="d-flex justify-content-center mt-5">Empty set!</p>;
          
          let inst_data = []
          
          for(let off of data.get_offerings){
            for(let inst of off.instructors){
              let instructor = inst_data.find(i => i.name === inst.name);

              if(!instructor){
                  inst_data.push({name:inst.name, offerings:1});
              }else{
                  instructor.offerings++;
              }
            }
          }

          if (inst_data.length == 0 || inst_data === undefined) return <p class="d-flex justify-content-center mt-5">Empty set!</p>;

          return (
            <div style={{ width: '100%', height: 300 }}>
                <ResponsiveContainer>
                    <ComposedChart
                        width={900}
                        height={400}
                        data={inst_data}
                        margin={{
                        top: 20, right: 20, bottom: 20, left: 20,
                        }}
                    >
                        <CartesianGrid stroke="#f5f5f5" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Area type="monotone" dataKey="offerings" fill="#8884d8" stroke="#8884d8" />
                        <Bar dataKey="offerings" barSize={20} fill="#413ea0" />
                    </ComposedChart>
                </ResponsiveContainer>       
            </div>
          );
        }}
      </Query>
    );
  }
}

export default Instructor;