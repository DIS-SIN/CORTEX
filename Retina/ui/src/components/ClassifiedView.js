import React, { Component } from 'react';
import {
  ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend,
} from 'recharts';


const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export default class ClassifiedView extends Component {

  render() {
    return (
      <ComposedChart
        layout="vertical"
        width={750}
        height={500}
        data={this.props.data.slice(0,10)}
        margin={{
          top: 20, right: 20, bottom: 20, left: 20,
        }}
      >
        <CartesianGrid stroke="#f5f5f5" />
        <XAxis type="number" />
        <YAxis dataKey="name" type="category" />
        <Tooltip />
        <Legend />
        <Bar dataKey="value" barSize={20} fill={COLORS[Math.floor((Math.random() * COLORS.length) + 1) % COLORS.length]} />
      </ComposedChart>
    );
  }
}
