import React from 'react';
import HTMLComment from './HTMLComment'
import DashMenu from './DashMenu';
import TagList from "./TagList";
import Registration from "./Registration";
import Daily from "./Daily";
import Department from "./Overview/DepartmentalView";
import ClassificationView from "./Overview/Section 1/ClassificationView";
import Response from "./Response";
import { Query } from "react-apollo";
import gql from "graphql-tag";
import { faReply, faGraduationCap, faTable, faRegistered} from '@fortawesome/free-solid-svg-icons';
import { TextField } from '@material-ui/core';
import DashBreadcrumbs from './DashBreadcrumbs';
import Section1 from './Overview/Section 1/Section';
import DepartmentalView from './Overview/DepartmentalView';

export default class DashBoard extends React.Component{

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

  getFirst = () => {
      return this.state.first.length > 0
          ? { first_contains: this.state.first }
          : {};
  };

  handleFirstChange = first => event => {
      const val = event.target.value;
      if(val){ 
          this.setState({
              [first]: parseInt(val)
          });
      }else{
          this.setState({
              [first]: 10
          });
      }
  };
  
  render(){
    return (
      <Query
        query={gql`query offeringsRangeQuery(
                $first: Int
                $from: String
                $to: String
            ){
              all_offs_data(from:$from, to:$to, first:$first){
                start_date,
                end_date,
                uid,
                week,
                month,
                status,
                registered_for{
                date,
                uid,
                no_show,
                status,
                learners{
                  classifications{
                    code
                  },
                  departments{
                    code,
                    name
                  }
                }
                },
                surveyed_for{
                date,
                uid,
                classification,
                department
                },
                instructors{
                  name
                },
                courses{
                  code,
                  title
                }
            }
        }
        `}
        variables={{
            from: this.state.from,
            to: this.state.to,
            first: this.state.first
        }}
        >
          {({ loading, error, data }) => {
            if (loading) return <p class="d-flex justify-content-center mt-5">Loading...</p>;
            if (error) return <p class="d-flex justify-content-center mt-5">Error</p>;

            var total_offerings = data.all_offs_data ? data.all_offs_data.length : 0;
            var total_registrations = 0;
            var total_responses = 0;

            
            var classificationData = [];
            var departmentalData = [];
            var instructorData = [];

            var registrations_per_course = [];

            for(let offering of data.all_offs_data){
                let course = registrations_per_course.find(c => c.code === offering.courses.code);
                
                if(!course){
                    let course_responses = offering.surveyed_for.length;
                    let course_registrations = offering.registered_for.length;
                    registrations_per_course.push({code: offering.courses.code, name: offering.courses.title, responses: course_responses, registrations: course_registrations, median: (course_responses + course_registrations) / 2});
                }else{
                  registrations_per_course[registrations_per_course.indexOf(course)].responses += offering.surveyed_for.length;
                  registrations_per_course[registrations_per_course.indexOf(course)].registrations += offering.registered_for.length;
                }
                
                total_responses += offering.surveyed_for.length;
                total_registrations += offering.registered_for.length;

                for(let inst of offering.instructors){
                  let instructor = instructorData.find(i => i.name === inst.name);

                  if(!instructor){
                    instructorData.push({name: inst.name, registrations: offering.registered_for.length, offerings: 1, courses: 1});
                  }else{
                    let index = instructorData.indexOf(instructor);
                    instructorData[index].registrations += offering.registered_for.length;
                    instructorData[index].offerings += offering.registered_for.length;
                    instructorData[index].registrations += offering.registered_for.length;
                  }
                }
            

                for(let reg of offering.registered_for){
                    let classification = classificationData.find(c => c.name === reg.learners[0].classifications[0].code);
                    let department = departmentalData.find(d => d.code === reg.learners[0].departments[0].code);                    
                    
                  if(!classification){
                    classificationData.push({name: reg.learners[0].classifications[0].code, registrations: 1});
                  }else{
                    let index = classificationData.indexOf(classification);
                    classificationData[index].registrations++;
                  }

                    if(!department){
                        departmentalData.push({code: reg.learners[0].departments[0].code, registrations: 1, name: reg.learners[0].departments[0].name});
                    }else{
                        let index = departmentalData.indexOf(department);
                        departmentalData[index].registrations++;
                    }
                }
            }

            console.log(classificationData, departmentalData);
          
          
          return (
            <div id="wrapper">
              <HTMLComment text="Menu" />
              <DashMenu />

              <div id="content-wrapper" class="ml-3">
                  <div class="row">
                    <DashBreadcrumbs className="col-lg-6"/>
                    <p class="col-lg-6">
                      <TextField
                          id="date"
                          label="From"
                          type="date"
                          value={this.state.from}
                          onChange={this.handleFromChange("from")}
                          defaultValue="2015-01-01"
                          className="flex wrap text-white"
                          InputLabelProps={{
                          shrink: true,
                          }}
                      />  
                      <TextField
                          id="date"
                          label="To"
                          type="date"
                          value={this.state.to}
                          onChange={this.handleFromChange("to")}
                          defaultValue="2019-08-09"
                          className="flex wrap text-white ml-1"
                          InputLabelProps={{
                          shrink: true,
                          }}
                      /> 
                      <TextField
                          id="date"
                          label="Size"
                          type="number"
                          value={this.state.first}
                          onChange={this.handleFirstChange("first")}
                          defaultValue="10"
                          className="flex wrap text-white ml-1"
                          InputLabelProps={{
                          shrink: true,
                          }}
                      />
                    </p>
                  </div>
                  
                  <Section1 classificationData={classificationData} />

                  <div class="card col-lg-12">
                    <div class="card-header bg-light">
                        <i class="fas fa-chart-area"></i>
                        Departmental data</div>
                    <div class="card-body">
                      <DepartmentalView data={departmentalData}/>
                    </div>
                    <div class="card-footer small text-muted">Updated yesterday at 11:59 PM</div>
                  </div>

                </div>
              </div>
          )}}
      </Query>
    );
  }
}
