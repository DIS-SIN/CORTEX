import React from 'react';
import HTMLComment from './HTMLComment'

export default class DashBreadcrumbs extends React.Component{

  constructor(props) {
    super(props);
  }
  
  render(){
    return (
      <div class={this.props.className}>
            <HTMLComment text="Page Heading" />
            <ol class="breadcrumb">
                <li class="breadcrumb-item">
                    <a href="#">Dashboard</a>
                </li>
                <li class="breadcrumb-item active">Overview</li>
            </ol>
      </div>
    );
  }
}