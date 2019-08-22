import React from 'react';
import { RadialBarChart, RadialBar, Legend } from 'recharts';

export default class Response extends React.Component {
  render() {
    return (
      <RadialBarChart width={400} height={300} cx={150} cy={150} innerRadius={20} outerRadius={140} barSize={10} data={this.props.data}>
        <RadialBar minAngle={15} label={{ position: 'insideStart', fill: '#fff' }} background clockWise dataKey="uv" />
        <Legend iconSize={10} width={120} height={140} layout="horizontal" verticalAlign="top"/>
      </RadialBarChart>
    );
  }
}
