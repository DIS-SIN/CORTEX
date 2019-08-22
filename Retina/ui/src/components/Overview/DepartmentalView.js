import React from 'react';
import {
    Radar, RadarChart, PolarGrid, Legend,
    PolarAngleAxis, PolarRadiusAxis,
  } from 'recharts';

export default class Department extends React.Component {
      
    render() {
        return (
            <RadarChart outerRadius={200} width={850} height={500} data={this.props.data}>
                <PolarGrid />
                <PolarAngleAxis dataKey="name" />
                <PolarRadiusAxis angle={30} domain={[0, 80]} />
                <Radar name="Responses" dataKey="responses" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                <Radar name="Registrations" dataKey="registrations" stroke="#f44336" fill="#f44336" fillOpacity={0.6} />
                <Legend />
            </RadarChart>
        );
    }
}
