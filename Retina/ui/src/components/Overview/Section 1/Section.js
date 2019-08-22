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
            from: this.props.from,
            to: this.props.to,
            first: this.props.first
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
            <div class="row ml-1">
              <div class="card col-lg-3">
                  <div class="card-header bg-light">
                      <i class="fas fa-chart-area"></i>
                      Classification data</div>
                  <div class="card-body">
                    <ClassificationView data={classificationData} />
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
          )}}
      </Query>
    )
  }
}
