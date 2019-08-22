import React from 'react';
import './App.css';
import DashBoard from '../Dashboard'
import Test from '../Test'
import NavBar from '../NavBar'
import HTMLComment from '../HTMLComment'

export default class App extends React.Component{
  
  render(){
    return (
      <div>
        <HTMLComment text="Topbar" />
        <NavBar />

        <HTMLComment text="Page Content" />
        <DashBoard />
      </div>
    );
  }
}
