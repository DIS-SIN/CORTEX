import React, { Component } from 'react';
import {
  ComposedChart, Line, Area, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend,
} from 'recharts';


export default class DepartmentalView extends Component {

  render() {
    return (
      <ComposedChart
        layout="vertical"
        width={1000}
        height={3000}
        data={this.props.data}
        margin={{
          top: 20, right: 20, bottom: 20, left: 20,
        }}
      >
        <CartesianGrid stroke="#f5f5f5" />
        <XAxis type="number" />
        <YAxis dataKey="code" type="category" />
        <Tooltip />
        <Legend />
        <Bar dataKey="registrations" barSize={20} fill="#82ca9d" />
      </ComposedChart>
    );
  }
}
