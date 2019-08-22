import React from 'react';
import HTMLComment from './HTMLComment'
import { TextField } from '@material-ui/core';
import DashBreadcrumbs from './DashBreadcrumbs';

export default class DashTopBar extends React.Component{

  constructor(props) {
    super(props);

    this.state = {
      from: "2018-01-01",
      to: "2019-01-01",
      first: 10
    };
  }

  getFrom = () => {
    return this.state.from.length > 0
        ? { year_contains: this.state.from }
        : {};
  };

  handleFromChange = from => event => {
      const val = event.target.value;
      this.setState({
        [from]: val
      });
  };

  getTo = () => {
      return this.state.to.length > 0
          ? { year_contains: this.state.to }
          : {};
  };

  handleFromChange = to => event => {
      const val = event.target.value;
      this.setState({
        [to]: val
      });
  };
  
  render(){
    return (
      <div>
          <HTMLComment text="DashTopBar" />
          <div class="row">
                <DashBreadcrumbs className="col-lg-12"/>
                
            </div>
          <HTMLComment text="End of DashTopBar" />
      </div>
    );
  }
}

