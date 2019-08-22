import React from "react";
import { Query } from "react-apollo";
import gql from "graphql-tag";
import { PieChart, Pie, Sector } from 'recharts';

const renderActiveShape = (props) => {
    const RADIAN = Math.PI / 180;
    const {
      cx, cy, midAngle, innerRadius, outerRadius, startAngle, endAngle,
      fill, payload, percent, value,
    } = props;
    const sin = Math.sin(-RADIAN * midAngle);
    const cos = Math.cos(-RADIAN * midAngle);
    const sx = cx + (outerRadius + 10) * cos;
    const sy = cy + (outerRadius + 10) * sin;
    const mx = cx + (outerRadius + 30) * cos;
    const my = cy + (outerRadius + 30) * sin;
    const ex = mx + (cos >= 0 ? 1 : -1) * 22;
    const ey = my;
    const textAnchor = cos >= 0 ? 'start' : 'end';
  
    return (
      <g>
        <text x={cx} y={cy} dy={8} textAnchor="middle" fill={fill}>{payload.name}</text>
        <Sector
          cx={cx}
          cy={cy}
          innerRadius={innerRadius}
          outerRadius={outerRadius}
          startAngle={startAngle}
          endAngle={endAngle}
          fill={fill}
        />
        <Sector
          cx={cx}
          cy={cy}
          startAngle={startAngle}
          endAngle={endAngle}
          innerRadius={outerRadius + 6}
          outerRadius={outerRadius + 10}
          fill={fill}
        />
        <path d={`M${sx},${sy}L${mx},${my}L${ex},${ey}`} stroke={fill} fill="none" />
        <circle cx={ex} cy={ey} r={2} fill={fill} stroke="none" />
        <text x={ex + (cos >= 0 ? 1 : -1) * 12} y={ey} textAnchor={textAnchor} fill="#333">{`Rsps ${value}`}</text>
        <text x={ex + (cos >= 0 ? 1 : -1) * 12} y={ey} dy={18} textAnchor={textAnchor} fill="#999">
          {`(Rate ${(percent * 100).toFixed(2)}%)`}
        </text>
      </g>
    );
};

class ClassDept extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            activeIndex: 0,
        };
    }
        
    onPieEnter = (data, index) => {
        this.setState({
            activeIndex: index,
        });
    };

    render() {
        return (
        <Query
            query={gql`query classificationsQuery(
                $code: String
                $from: String
                $to: String
            ){
                get_offerings(code:$code, from:$from, to:$to){
                    registered_for{
                        learners{
                            classifications{
                                code
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

                let class_data = [];
                
                for(let off of data.get_offerings){
                    for(let reg of off.registered_for){
                        for(let l of reg.learners){
                            for(let c of l.classifications){
                                let classification = class_data.find(d => d.name === c.code);

                                if(!classification){
                                    class_data.push({name:c.code, count: 1});
                                }else{
                                    classification.count++;
                                }
                            }
                        }
                    }
                }

                if (class_data.length == 0 || class_data === undefined) return <p class="d-flex justify-content-center mt-5">Empty set!</p>;

                return (
                    <PieChart width={500} height={400}>
                        <Pie
                        activeIndex={this.state.activeIndex}
                        activeShape={renderActiveShape}
                        data={class_data}
                        cx={200}
                        cy={200}
                        innerRadius={60}
                        outerRadius={80}
                        fill="#f26e40"
                        dataKey="count"
                        onMouseEnter={this.onPieEnter}
                        />
                    </PieChart>
                );
            }}
        </Query>
        );
    }
    }

export default ClassDept;