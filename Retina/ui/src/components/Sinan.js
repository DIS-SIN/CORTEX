import React from 'react';
import './App/App.css';
import DashTopBar from './DashTopBar'
import Test from './Test'
import HTMLComment from './HTMLComment'

export default class App extends React.Component{
  
  render(){
    return (
      <div>
        <HTMLComment text="Topbar" />
        <DashTopBar />

        <HTMLComment text="Page Content" />
        <Test />
      </div>
    );
  }
}
