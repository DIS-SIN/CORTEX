import React from 'react';
import { Query } from "react-apollo";
import gql from "graphql-tag";
import ClassificationView from './ClassificationView';
import InstructorView from '../InstructorView';

export default class Section1 extends React.Component{

  constructor(props) {
    super(props);
  }
  
  render(){
    return (
        <div class="row ml-1 mb-5">
          <div class="card col-lg-3">
              <div class="card-header bg-light">
                  <i class="fas fa-chart-area"></i>
                  Classification data</div>
              <div class="card-body">
                <ClassificationView data={this.props.classificationData} />
              </div>
              <div class="card-footer small text-muted">Updated yesterday at 11:59 PM</div>
          </div>

          <div class="card col-lg-3 ml-3">
              <div class="card-header bg-light">
                  <i class="fas fa-chart-area"></i>
                  Instructor data</div>
              <div class="card-body">
                <InstructorView />
              </div>
              <div class="card-footer small text-muted">Updated yesterday at 11:59 PM</div>
          </div>
        </div>
      )}
  }

