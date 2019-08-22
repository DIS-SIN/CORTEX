import React from 'react';
import { XAxis, YAxis, CartesianGrid, Tooltip, AreaChart, Area } from 'recharts';

const style = {
    top: 0,
    left: 350,
    lineHeight: '24px',
  };

export default class Daily extends React.Component {
  render() {
    return (
        <AreaChart
          width={600}
          height={200}
          data={this.props.data}
          syncId="anyId"
          margin={{
            top: 10, right: 30, left: 0, bottom: 0,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis type="number" domain={[0, 100]}/>
          <Tooltip />
          <Area type="monotone" dataKey="rate" stroke="#82ca9d" fill="#82ca9d" />
        </AreaChart>
    );
  }
}
