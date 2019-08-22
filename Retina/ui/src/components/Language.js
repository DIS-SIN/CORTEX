import React from "react";
import { Query } from "react-apollo";
import gql from "graphql-tag";
import {
    PieChart, Pie, Tooltip, Cell,
  } from 'recharts';

class Language extends React.Component {
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
        query={gql`query languageQuery(
            $code: String
            $from: String
            $to: String
        ){
          get_offerings(code:$code, from:$from, to:$to){
            languages{
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
            if (error) return <p class="d-flex justify-content-center mt-5">Error</p>;
            if (!data.get_offerings) return <p class="d-flex justify-content-center mt-5">Empty set!</p>;
            let lang_data = []

            for(let off of data.get_offerings){
                for(let lang of off.languages){
                    let language = lang_data.find(l => l.name === lang.name);

                    if(!language){
                        lang_data.push({name:lang.name, count:1});
                    }else{
                        language.count++;
                    }
                }
            }

            if (lang_data.length == 0 || lang_data === undefined) return <p class="d-flex justify-content-center mt-5">Empty set!</p>;

            const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];
            const RADIAN = Math.PI / 180;
            const renderCustomizedLabel = ({
            cx, cy, midAngle, innerRadius, outerRadius, percent, index,
            }) => {
            const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
            const x = cx + radius * Math.cos(-midAngle * RADIAN);
            const y = cy + radius * Math.sin(-midAngle * RADIAN);

            return (
                <text x={x} y={y} fill="white" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central">
                {`${(percent * 100).toFixed(0)}%`}
                </text>
            );
            };

          return (
            <PieChart width={800} height={400} onMouseEnter={this.onPieEnter}>
                <Pie
                data={lang_data}
                cx={120}
                cy={200}
                label={renderCustomizedLabel}
                innerRadius={60}
                outerRadius={120}
                fill="#8884d8"
                paddingAngle={5}
                dataKey="count"
                >                   
                {
                    lang_data.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)
                }
                </Pie>
                <Tooltip />
            </PieChart>
          );
        }}
      </Query>
    );
  }
}

export default Language;