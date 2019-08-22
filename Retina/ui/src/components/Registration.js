import React from 'react';
import {
  ComposedChart, Line, Area, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend,
} from 'recharts';

export default class Registration extends React.Component {
  render() {
    return (
        <ComposedChart
        width={750}
        height={400}
        data={this.props.data}
        margin={{
          top: 20, right: 80, bottom: 20, left: 20,
        }}>
            <CartesianGrid stroke="#ddffff" />
            <XAxis dataKey="code" label={{ value: 'Course code', position: 'insideBottomRight', offset: 0 }} />
            <YAxis label={{ value: 'Index', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Area type="monotone" dataKey="registrations" fill="#8884d8" stroke="#8884d8" />
            <Bar dataKey="responses" barSize={20} fill="#413ea0" />
            <Line type="monotone" dataKey="median" stroke="#ff7300" />
        </ComposedChart>
    );
  }
}
