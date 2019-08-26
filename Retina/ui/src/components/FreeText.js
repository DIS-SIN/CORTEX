import React from 'react';
import { TableBody, Typography, CardActions, Button, Grid, TableRow, TableCell } from '@material-ui/core';

export default class FreeText extends React.Component{
  
    render(){
        return (
            <TableBody>
            {this.props.data.slice(0,5).map(n => {
              return (
                <TableRow key={n.uid}>
                  <TableCell component="th" scope="row">
                    {n.name}
                  </TableCell>
                  <TableCell numeric>
                    {n.value}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        )}
  }