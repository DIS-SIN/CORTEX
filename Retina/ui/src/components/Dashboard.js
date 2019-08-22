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
                    status
                    },
                    surveyed_for{
                    date,
                    uid,
                    classification,
                    department
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
            var total_responses = 0;
            var total_registrations = 0;

            var total_responses_rate_per_day = 0;

            var responseData = [];
            var dailyData = [];
            var classificationData = [];
            var departmentalData = [];

            var responses_per_day = [];
            var responses_per_course = [];
            var responses_per_classification = [];
            var responses_per_department = [];

            for(let offering of data.all_offs_data){
                let course = responses_per_course.find(c => c.code === offering.course_code);
                
                if(!course){
                    let course_responses = offering.surveyed_for.length;
                    let course_registrations = offering.registered_for.length;
                    responses_per_course.push({code: offering.course_code, name: offering.course_name, responses: course_responses, registrations: course_registrations, median: (course_responses + course_registrations) / 2});
                }else{
                    responses_per_course[responses_per_course.indexOf(course)].responses += offering.surveyed_for.length;;
                    responses_per_course[responses_per_course.indexOf(course)].registrations += offering.registered_for.length;
                }
                
                total_responses += offering.surveyed_for.length;
                total_registrations += offering.registered_for.length;

                let offering_registrations = offering.registered_for.length;
                let daily_responses = 0;
            
                let classification_responses = 0;
                let department_responses = 0;
            

                for(let response of offering.surveyed_for){
                    let day = responses_per_day.find(r => r.day === response.date);
                    let classification = responses_per_classification.find(c => c.classification === response.classification);
                    let department = responses_per_department.find(d => d.department === response.department);
                    

                    if(!day){
                    daily_responses = 1;
                    responses_per_day.push({day: response.date, offerings: [offering.uid], responses: daily_responses, registrations: offering_registrations});
                    }else{
                    responses_per_day[responses_per_day.indexOf(day)].responses++;
                        if(!responses_per_day[responses_per_day.indexOf(day)].offerings.includes(offering.uid)){
                        responses_per_day[responses_per_day.indexOf(day)].offerings.push(offering.uid);
                        responses_per_day[responses_per_day.indexOf(day)].registrations += offering_registrations;
                        }
                    }
                    
                    
                    if(!classification){
                    responses_per_classification.push({classification: response.classification, offerings: [offering.uid], count: 1, registrations: offering_registrations});
                    }else{
                    let index = responses_per_classification.indexOf(classification);
                    responses_per_classification[index].count++;
                      if(!responses_per_classification[index].offerings.includes(offering.uid)){
                          responses_per_classification[index].offerings.push(offering.uid);
                          responses_per_classification[index].registrations += offering_registrations;
                      }
                    }

                    if(!department){
                        department_responses = 1;
                        responses_per_department.push({department: response.department, offerings: [offering.uid], responses: department_responses, registrations: offering_registrations});
                    }else{
                        let index = responses_per_department.indexOf(department);
                        responses_per_department[index].responses++;
                        if(!responses_per_department[index].offerings.includes(offering.uid)){
                            responses_per_department[index].offerings.push(offering.uid);
                            responses_per_department[index].registrations += offering_registrations;
                        }
                    }
                }
            }


            for(let daily_avg of responses_per_day){
                total_responses_rate_per_day += (daily_avg.responses / daily_avg.registrations);
                dailyData.push({
                    name: daily_avg.day, rate: ((daily_avg.responses / daily_avg.registrations) * 100).toFixed(2), registrations: daily_avg.registrations});
            }


            for(let class_avg of responses_per_classification){
            classificationData.push({
                name: class_avg.classification, responses: class_avg.responses , registrations: class_avg.registrations});
            }

            for(let dept_avg of responses_per_department){
            departmentalData.push({
                name: dept_avg.department, responses: dept_avg.responses , registrations: dept_avg.registrations});
            }


            responseData.push({name: 'Daily', uv: ((total_responses_rate_per_day / responses_per_day.length) * 100).toFixed(2), fill: '#8884d8'});
            responseData.push({name: 'Overall', uv: ((total_responses / total_registrations) * 100).toFixed(2), fill: '#ffc658'});

            let tagsData = [{label: "Courses", size: responses_per_course.length, icon: faGraduationCap, color: 'primary'}, {label: "Offerings", size: total_offerings, icon: faTable, color: 'success'}, {label: "Registrations", size: total_registrations, icon: faRegistered, color: 'danger'}, {label: "Responses", size: total_responses, icon: faReply, color: 'warning'}];
          
          
          return (
            <div id="wrapper">
              <HTMLComment text=" Menu" />
              <DashMenu />

              <div id="content-wrapper">
                <div class="container">
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
                  <TagList tagsData={tagsData}/>
                  
                  <div class="card">
                    <div class="card-header bg-dark text-white">
                      <i class="fas fa-chart-area"></i>
                      Avg response rate<span class="float-right">Daily response rate</span></div>
                    <div class="card-body">
                      <div class="row">
                        <div class="col-sm-3">
                          <Response data={responseData}/>
                        </div>
                        <div class="col-sm-9 text-right">
                          <Daily data={dailyData.slice(0,5)}/>
                        </div>
                      </div>
                    </div>
                    <div class="card-footer small text-muted">Updated yesterday at 11:59 PM</div>
                  </div>

                  <div class="card mt-5">
                    <div class="card-header bg-dark text-white">
                      <i class="fas fa-chart-area"></i>
                      Registrations / Responses per course<span class="float-right">Classifications response rate</span></div>
                    <div class="card-body">
                      <div class="row">
                        <div class="col-sm-8">
                        <Registration data={responses_per_course.slice(0,15)}/>
                        </div>
                        <div class="col-sm-4 text-right">
                          <ClassificationView data={classificationData}/>
                        </div>
                      </div>
                    </div>
                    <div class="card-footer small text-muted">Updated yesterday at 11:59 PM</div>
                  </div>

                  <div class="card mt-5">
                    <div class="card-header bg-dark text-white">
                      <i class="fas fa-chart-area"></i>
                      Registrations / Responses per department</div>
                    <div class="card-body">
                      <Department data={departmentalData.slice(0,15)}/>
                    </div>
                    <div class="card-footer small text-muted">Updated yesterday at 11:59 PM</div>
                  </div>

                </div>
              </div>
            </div>
          )}}
      </Query>
    );
  }
}
