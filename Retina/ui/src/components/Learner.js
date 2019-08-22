import React from "react";
import { Query } from "react-apollo";
import gql from "graphql-tag";
import {
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  } from 'recharts';

class Learner extends React.Component {
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
        query={gql`query offeringsRangeQuery(
            $code: String
            $from: String
            $to: String
        ){
            get_offerings(code:$code, from:$from, to:$to){
                registered_for{
                    learners{
                        departments{
                            name
                        }
                    }
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

            let dept_data = [];
            
            for(let off of data.get_offerings){
                for(let reg of off.registered_for){
                    for(let l of reg.learners){
                        for(let dept of l.departments){
                            let department = dept_data.find(d => d.name === dept.name);

                            if(!department){
                                dept_data.push({name:dept.name, count: 1});
                            }else{
                                department.count++;
                            }
                        }
                    }
                }
            }

            if (dept_data.length == 0 || dept_data === undefined) return <p class="d-flex justify-content-center mt-5">Empty set!</p>;

            return (
                <RadarChart cx={500} cy={250} outerRadius={150} width={900} height={500} data={dept_data.slice(0,15)}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="name" />
                  <PolarRadiusAxis />
                  <Radar name="Learners" dataKey="count" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                </RadarChart>
            );
        }}
      </Query>
    );
  }
}

export default Learner;